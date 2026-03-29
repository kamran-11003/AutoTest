"""
Adaptive Test Runner (Master Orchestrator)
Combines BaseRunner + HeuristicOracle + LLMOracle + DQNAgent to run a full
test suite adaptively, respecting API budget and time limits.

Usage:
    runner = AdaptiveRunner(api_budget=30, time_limit_s=600, rl_mode=True)
    report = await runner.execute(test_suite_path="data/generated_tests/suite.json")
"""

import sys
import time
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution.test_result  import TestResult, TestStatus, OracleMethod, ExecutionReport
from execution.base_runner  import BaseRunner
from execution.llm_oracle   import LLMOracle
from execution.rl_agent.dqn_agent import DQNAgent
from execution.reporter     import Reporter
from execution.cache_manager import TestCacheManager
from execution.failure_probability_scorer import TestFailureScorer
from execution.test_subtype_classifier import TestSubtypeClassifier
from execution.rl_performance_tracker import RLPerformanceTracker
from execution.heuristics_logger import HeuristicsLogger
from execution.rl_heuristics_optimizer import RLHeuristicsOptimizer

_RL_OPT_SCORES_FILE = Path("data/rl_optimizations/score_updates.jsonl")
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# Test priority order (higher = run first)
PRIORITY = {"BVA": 5, "ECP": 4, "StateTransition": 3, "DecisionTable": 2, "UseCase": 1}


class AdaptiveRunner:
    """
    Runs a loaded test suite with adaptive oracle selection.

    Args:
        api_budget:    Max LLM oracle calls allowed
        time_limit_s:  Wall-clock cutoff in seconds (0 = no limit)
        rl_mode:       If False, always use heuristic + LLM for conf<70 (no RL)
        headless:      Playwright headless mode
        progress_cb:   Optional async callback(current, total, result) for live UI updates
    """

    def __init__(
        self,
        api_budget:   int  = 30,
        time_limit_s: float = 600,
        rl_mode:      bool  = True,
        headless:     bool  = True,
        progress_cb:  Optional[Callable] = None,
        use_cache:    bool  = True,
        use_scoring:  bool  = True,
    ):
        self.api_budget   = api_budget
        self.time_limit_s = time_limit_s
        self.rl_mode      = rl_mode
        self.headless     = headless
        self.progress_cb  = progress_cb
        self.use_cache    = use_cache
        self.use_scoring  = use_scoring

        self.runner   = BaseRunner()
        self.llm      = LLMOracle()
        self.agent    = DQNAgent() if rl_mode else None
        self.reporter = Reporter()
        
        # Initialize cache manager for test result caching
        self.cache = TestCacheManager() if use_cache else None
        
        # Initialize failure probability scorer for test prioritization
        self.scorer = TestFailureScorer() if use_scoring else None
        
        # Initialize performance tracker for RL metrics logging
        self.perf_tracker = RLPerformanceTracker()
        
        # Initialize heuristics logger for transparency
        self.heuristics_logger = HeuristicsLogger()
        
        # Initialize RL heuristics optimizer for score updates
        self.heuristics_optimizer = RLHeuristicsOptimizer()

        # [RL Goal 2] Load persisted risk-score updates from previous runs
        self._load_persisted_risk_scores()

    # ── Public entry point ─────────────────────────────────────────────────

    async def execute(
        self,
        test_suite: Dict,
        crawl_id:   str = "unknown",
    ) -> ExecutionReport:
        """
        Run all test cases in the suite.

        Args:
            test_suite: Loaded test suite dict (from test_storage or direct JSON)
            crawl_id:   Identifier used for report filenames

        Returns:
            ExecutionReport (also saved to data/test_results/)
        """
        all_tests = self._flatten_and_sort(test_suite)
        total     = len(all_tests)

        if total == 0:
            logger.warning("No test cases found in suite")
            return ExecutionReport(crawl_id=crawl_id, stop_reason="no_tests")

        report = ExecutionReport(
            crawl_id = crawl_id,
            total    = total,
            rl_mode  = self.rl_mode,
        )

        start_wall = time.perf_counter()

        # ── Tracking variables ─────────────────────────────────────────
        consecutive_passes     = 0
        uncertain_count        = 0
        llm_confidences: List[float] = []
        # Track consecutive LLM quota failures. If ALL keys are exhausted
        # we stop attempting LLM for the rest of the session to save time.
        _llm_consec_fails  = 0
        _llm_all_exhausted = False
        _LLM_FAIL_LIMIT    = 3   # after this many consecutive quota hits, give up LLM
        # Track consecutive network failures (ERR_CONNECTION_REFUSED etc.).
        # If the server is simply down, abort quickly rather than running all
        # tests and hitting the unrelated hard-stop on uncertain_count.
        _consec_network_errors = 0
        _NETWORK_FAIL_LIMIT    = 3

        # ── Launch Playwright ──────────────────────────────────────────
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            page    = await context.new_page()

            for idx, test_case in enumerate(all_tests):
                elapsed = time.perf_counter() - start_wall

                # ── Time / budget guards ───────────────────────────────
                if self.time_limit_s and elapsed >= self.time_limit_s:
                    report.stop_reason = "time_limit"
                    logger.info("Time limit reached — stopping")
                    break

                if report.api_calls_used >= self.api_budget:
                    report.stop_reason = "budget_exhausted"
                    logger.info("API budget exhausted — stopping")
                    break

                # ── [RL Goal 1] Adaptive early stop ──────────────────────
                # Threshold adapts from historical pass-rate trends stored by
                # RLPerformanceTracker: easy sites → stop sooner; hard sites
                # → wait longer before giving up.
                _stop_threshold = self._compute_early_stop_threshold()
                if uncertain_count >= _stop_threshold and idx >= max(10, total // 10):
                    recent_results = [r for r in report.results[-_stop_threshold:]
                                      if r.status == TestStatus.ERROR]
                    if len(recent_results) >= _stop_threshold:
                        report.stop_decisions += 1
                        report.stop_reason = "rl_stop"
                        logger.info(
                            f"[RL Goal 1] Adaptive early stop at test {idx+1}/{total}: "
                            f"oracle unclear for last {_stop_threshold} tests "
                            f"(threshold={_stop_threshold}, "
                            f"hist_runs={len(self.perf_tracker.snapshots)})"
                        )
                        break

                # ── RL: choose oracle (heuristic=0 or LLM=1) ──────────
                # The neural net NEVER decides to stop — that is a hard rule.
                if self.rl_mode and self.agent:
                    state = DQNAgent.build_state(
                        tests_run          = idx,
                        total_tests        = total,
                        failures           = report.failed,
                        consecutive_passes = consecutive_passes,
                        avg_llm_confidence = (sum(llm_confidences) / len(llm_confidences)) if llm_confidences else 50.0,
                        uncertain_count    = uncertain_count,
                        api_calls_used     = report.api_calls_used,
                        api_budget         = self.api_budget,
                        time_elapsed_s     = elapsed,
                        time_limit_s       = self.time_limit_s or 3600,
                        test_case          = test_case,
                    )
                    action = self.agent.choose_action(state)  # returns 0 or 1 only
                else:
                    state  = None
                    action = 0

                # ── [RL Goal 3] Pattern-learning oracle override ───────
                # If accumulated subtype history shows heuristic is reliable
                # for this test class, skip LLM even when DQN says action=1.
                # Conversely, force LLM when heuristic historically fails.
                if self.rl_mode and not _llm_all_exhausted:
                    _tc_subtype = (
                        self.scorer.subtype_classifier.classify(test_case).subtype
                        if self.scorer and self.scorer.subtype_classifier
                        else "unknown"
                    )
                    _st = self.heuristics_logger.subtype_stats.get(_tc_subtype, {})
                    _h_uses   = _st.get("heuristic_uses", 0)
                    _l_uses   = _st.get("llm_uses", 0)
                    _h_passed = _st.get("heuristic_passed", 0)
                    _l_passed = _st.get("llm_passed", 0)
                    if _h_uses >= 5:
                        _h_rate = _h_passed / _h_uses
                        if _h_rate >= 0.85 and action == 1:
                            # Heuristic proven sufficient → save API call
                            action = 0
                            report.pattern_overrides += 1
                            logger.debug(
                                f"[RL Goal 3] Pattern override LLM→Heuristic "
                                f"for {_tc_subtype} (heur={_h_rate:.0%})"
                            )
                        elif _h_rate < 0.45 and _l_uses >= 5:
                            _l_rate = _l_passed / _l_uses
                            if _l_rate >= 0.75 and action == 0:
                                # Heuristic proven poor, LLM proven better → use LLM
                                action = 1
                                report.pattern_overrides += 1
                                logger.debug(
                                    f"[RL Goal 3] Pattern override Heuristic→LLM "
                                    f"for {_tc_subtype} (heur={_h_rate:.0%}, llm={_l_rate:.0%})"
                                )
                test_id = test_case.get("id", "unknown")
                form_url = test_case.get("form_url", "")
                cached_result = None
                
                if self.use_cache and self.cache:
                    cached_result = self.cache.get_cached_result(test_id)
                    if cached_result:
                        logger.info(f"[{test_id}] Using cached result (status: {cached_result['status']})")
                        # Create test result from cache
                        result = TestResult(
                            test_id=test_id,
                            status=TestStatus.PASSED if cached_result["status"] == "passed" else TestStatus.FAILED,
                            duration_ms=cached_result.get("execution_time_ms", 0),
                            oracle_method=OracleMethod.HEURISTIC,
                            confidence=cached_result.get("confidence", 100),
                            evidence=f"[CACHED] {cached_result.get('evidence', 'Cached result')}",
                            test_type=test_case.get("type", ""),
                            form_url=form_url,
                        )
                        report.skipped += 1
                        report.results.append(result)
                        
                        # Simulate heuristic output
                        heuristic = {
                            "confidence": cached_result.get("confidence", 100),
                            "outcome": "success" if cached_result["status"] == "passed" else "error",
                            "evidence": cached_result.get("evidence", ""),
                        }
                        conf = heuristic["confidence"]
                        unclear = False
                        
                        # Skip to next test (don't execute runner or oracles)
                        if self.progress_cb:
                            await self.progress_cb(idx + 1, total, result)
                        continue

                # ── Execute test ───────────────────────────────────────
                try:
                    result, heuristic = await self.runner.run(page, test_case)
                except Exception as e:
                    logger.error(f"Runner crashed on {test_case.get('id')}: {e}")
                    report.errors += 1
                    report.results.append(TestResult(
                        test_id=test_case.get("id", "?"),
                        status=TestStatus.ERROR,
                        duration_ms=0,
                        error_message=str(e),
                        test_type=test_case.get("type", ""),
                        form_url=test_case.get("form_url", ""),
                    ))
                    continue

                conf    = heuristic["confidence"]
                unclear = heuristic["outcome"] == "unclear"

                # ── Oracle decision ────────────────────────────────────
                use_llm = False
                _llm_forced_off_this_step = False
                if _llm_all_exhausted:
                    # All API keys exhausted this session — skip LLM entirely
                    use_llm = False
                    report.heuristic_decisions += 1
                    if action == 1:
                        # Agent wanted LLM but quota gone — don't penalise this
                        _llm_forced_off_this_step = True
                elif self.rl_mode and self.agent and state is not None:
                    use_llm = (action == 1)
                    if action == 0:
                        report.heuristic_decisions += 1
                    else:
                        report.llm_decisions += 1
                else:
                    # Non-RL mode: call LLM whenever heuristic is uncertain
                    use_llm = (conf < 70 or unclear)

                if use_llm and report.api_calls_used < self.api_budget:
                    llm_result = await self.llm.evaluate(
                        page,
                        test_case,
                        screenshot_path=result.screenshot_path,
                    )
                    report.api_calls_used += 1
                    report.api_cost       += 0.002
                    llm_confidences.append(float(llm_result["confidence"]))

                    # Update result with LLM verdict.
                    # If LLM is also unclear (quota exhausted, parse error, etc.)
                    # fall back to the heuristic's own verdict rather than
                    # leaving the test as ERROR.
                    llm_outcome = llm_result["outcome"]

                    if llm_outcome in ("success", "error"):
                        result.oracle_method = OracleMethod.LLM
                        result.confidence    = llm_result["confidence"]
                        result.evidence      = llm_result["evidence"]
                        result.status = (TestStatus.PASSED
                                         if llm_outcome == "success"
                                         else TestStatus.FAILED)
                        _llm_consec_fails = 0   # successful call — reset
                    else:
                        # LLM unclear / failed — keep heuristic's verdict.
                        # The heuristic status was already set in base_runner.
                        result.oracle_method = OracleMethod.HEURISTIC
                        result.evidence = (
                            f"LLM unclear ({llm_result['evidence']}) "
                            f"— heuristic fallback: {heuristic['evidence']}"
                        )
                        # Count consecutive quota failures to detect full exhaustion
                        _llm_consec_fails += 1
                        if _llm_consec_fails >= _LLM_FAIL_LIMIT:
                            _llm_all_exhausted = True
                            logger.warning(
                                f"LLM disabled for session after "
                                f"{_llm_consec_fails} consecutive failures "
                                f"(all keys quota-exhausted). "
                                f"Heuristic-only for remaining tests."
                            )

                # ── Update tracking ────────────────────────────────────
                _is_network_error = (
                    result.status == TestStatus.ERROR
                    and result.error_message is not None
                    and "net::ERR_" in result.error_message
                )
                if _is_network_error:
                    _consec_network_errors += 1
                    if _consec_network_errors >= _NETWORK_FAIL_LIMIT:
                        report.stop_reason = "server_unreachable"
                        logger.error(
                            f"Server unreachable after {_consec_network_errors} "
                            f"consecutive network errors — aborting run. "
                            f"Please start the test server and try again."
                        )
                        report.errors += 1
                        report.results.append(result)
                        break
                else:
                    _consec_network_errors = 0  # reset on any non-network result

                if result.status == TestStatus.PASSED:
                    report.passed      += 1
                    consecutive_passes += 1
                elif result.status == TestStatus.FAILED:
                    report.failed      += 1
                    consecutive_passes  = 0
                elif result.status == TestStatus.ERROR:
                    report.errors      += 1
                    consecutive_passes  = 0
                    # Only count as oracle-uncertain if it's NOT a plain network
                    # failure — connection refused is infrastructure, not ambiguity.
                    if unclear and not _is_network_error:
                        uncertain_count += 1
                else:
                    report.skipped += 1

                report.results.append(result)
                
                # ── Store result to cache ──────────────────────────────
                if self.use_cache and self.cache and result.status == TestStatus.PASSED:
                    # Only cache passed results (failed/error results are typically test infrastructure issues)
                    self.cache.store_result(
                        test_id=result.test_id,
                        status=result.status.value,
                        execution_time_ms=result.duration_ms,
                        form_url=result.form_url,
                        confidence=result.confidence,
                        oracle_method=result.oracle_method.value,
                        evidence=result.evidence,
                    )

                # ── RL: compute reward + learn ─────────────────────────
                if self.rl_mode and self.agent and state is not None:
                    reward = self._compute_reward(result, action, conf, idx, total, report, _llm_forced_off_this_step)
                    
                    # Log RL outcome per test subtype
                    test_subtype = self.scorer.subtype_classifier.classify(test_case).subtype if self.scorer and self.scorer.subtype_classifier else "unknown"
                    self.heuristics_logger.log_rl_outcome(
                        test_id=result.test_id,
                        subtype=test_subtype,
                        rl_action=action,
                        result_status=result.status.value,
                        reward=reward,
                    )
                    
                    next_elapsed = time.perf_counter() - start_wall
                    next_state   = DQNAgent.build_state(
                        tests_run          = idx + 1,
                        total_tests        = total,
                        failures           = report.failed,
                        consecutive_passes = consecutive_passes,
                        avg_llm_confidence = (sum(llm_confidences) / len(llm_confidences)) if llm_confidences else 50.0,
                        uncertain_count    = uncertain_count,
                        api_calls_used     = report.api_calls_used,
                        api_budget         = self.api_budget,
                        time_elapsed_s     = next_elapsed,
                        time_limit_s       = self.time_limit_s or 3600,
                        test_case          = test_case,
                    )
                    done = (idx + 1 >= total)
                    self.agent.remember(state, action, reward, next_state, done)
                    self.agent.replay()

                # ── Progress callback ──────────────────────────────────
                if self.progress_cb:
                    await self.progress_cb(idx + 1, total, result)

                logger.info(
                    f"[{idx+1}/{total}] {result.test_id} → {result.status.value} "
                    f"(conf={result.confidence}%, oracle={result.oracle_method.value})"
                )

            await browser.close()

        # ── Finalise report ────────────────────────────────────────────
        report.duration_s = round(time.perf_counter() - start_wall, 2)
        if report.stop_reason == "completed" and len(report.results) < total:
            report.stop_reason = "partial"

        # Save RL model (learns across sessions)
        if self.rl_mode and self.agent:
            self.agent.save()
        
        # Record execution metrics in performance tracker
        if self.rl_mode and self.agent:
            pass_rate = report.passed / report.total if report.total > 0 else 0
            factor_changes = []  # Would be populated if you're adjusting factors dynamically
            
            self.perf_tracker.record_execution(
                pass_rate=pass_rate,
                heuristic_decisions=report.heuristic_decisions,
                llm_decisions=report.llm_decisions,
                api_calls_used=report.api_calls_used,
                api_cost=report.api_cost,
                execution_time_seconds=report.duration_s,
                epsilon=self.agent.epsilon,
                q_learning_rate=self.agent.learning_rate,
                discount_factor=self.agent.discount_factor,
                factor_changes=factor_changes,
                notes=f"Stop reason: {report.stop_reason} | {report.passed}/{report.total} passed"
            )
            
            # Generate and save summary report
            self.perf_tracker.save_summary_report()
            logger.info(f"Performance metrics saved to {self.perf_tracker.output_dir}")
            
            # Generate and save heuristics analysis report
            self.heuristics_logger.save_analysis_report()
            stats = self.heuristics_logger.get_statistics()
            logger.info(
                f"Heuristics analysis: {stats['total_tests']} tests, "
                f"{stats['heuristic_percentage']:.1f}% heuristic, "
                f"{stats['llm_percentage']:.1f}% LLM, "
                f"avg reward: {stats['average_reward']:+.2f}"
            )
            
            # Compute heuristic score updates based on RL learning
            subtype_stats = self.heuristics_logger.get_subtype_statistics()
            if subtype_stats:
                self.heuristics_optimizer.compute_updates(subtype_stats)
                self.heuristics_optimizer.save_report()
                opt_stats = self.heuristics_optimizer.get_statistics()
                logger.info(
                    f"Heuristics optimization: {opt_stats.get('total_subtypes_optimized', 0)} subtypes updated | "
                    f"Risk increases: {opt_stats.get('risk_increases', 0)} | "
                    f"Risk decreases: {opt_stats.get('risk_decreases', 0)} | "
                    f"Avg change: {opt_stats.get('average_risk_change', 0):+.4f}"
                )

        # Write HTML + JSON report
        self.reporter.write(report, crawl_id)

        logger.info(
            f"Execution complete: {report.passed}/{report.total} passed "
            f"| {report.api_calls_used} LLM calls (${report.api_cost:.3f}) "
            f"| stop_reason={report.stop_reason}"
        )
        return report

    # ── Helpers ────────────────────────────────────────────────────────────

    def _flatten_and_sort(self, suite: Dict) -> List[dict]:
        """
        Flatten {type: [cases]} into a priority-sorted flat list.
        Apply failure probability scoring to prioritize risky tests first.
        """
        flat = []
        test_cases = suite.get("test_cases", suite)   # handle both formats
        if isinstance(test_cases, dict):
            for test_type, cases in test_cases.items():
                if isinstance(cases, list):
                    for c in cases:
                        if isinstance(c, dict):
                            c.setdefault("type", test_type.upper().replace(" ", ""))
                            flat.append(c)
        elif isinstance(test_cases, list):
            flat = test_cases

        # Use failure probability scoring if enabled
        if self.use_scoring and self.scorer:
            scores = self.scorer.score_tests(flat)
            # Create lookup dict for priority
            priority_map = {s.test_id: s.priority for s in scores}
            # Sort by probability score (ascending priority = higher risk first)
            flat.sort(key=lambda x: priority_map.get(x.get("id", ""), 9999))
            
            # Log all heuristic factors for each test
            for score in scores:
                test_case = next((t for t in flat if t.get("id") == score.test_id), None)
                if test_case:
                    subtype_info = self.scorer.subtype_classifier.classify(test_case)
                    
                    # Calculate individual factors
                    input_risk = self.scorer._assess_input_complexity(test_case.get("test_data", {}))
                    field_risk = self.scorer._assess_field_types(test_case.get("form", {}), test_case.get("test_data", {}))
                    form_risk = self.scorer._assess_form_complexity(test_case.get("form", {}))
                    validation_risk = self.scorer._assess_validation_rules(test_case.get("form", {}))
                    boundary_risk = self.scorer._assess_boundary_values(test_case)
                    
                    self.heuristics_logger.log_heuristics(
                        test_id=score.test_id,
                        test_type=score.test_type,
                        subtype=subtype_info.subtype,
                        subtype_risk=subtype_info.base_risk,
                        input_complexity_risk=input_risk,
                        field_type_risk=field_risk,
                        form_complexity_risk=form_risk,
                        validation_rules_risk=validation_risk,
                        boundary_values_risk=boundary_risk,
                        final_failure_probability=score.failure_probability,
                        priority=score.priority,
                        factors_explanation=score.risk_factors,
                    )
                    
                    # Record initial risk scores for heuristics optimizer
                    self.heuristics_optimizer.record_initial_scores(
                        subtype=subtype_info.subtype,
                        test_type=score.test_type,
                        initial_risk=subtype_info.base_risk,
                        initial_confidence=0.75,  # Default confidence in scoring
                    )
            
            # Show priority report
            logger.info(self.scorer.report_scores(scores, limit=10))
            
            # Show subtype classification report
            if self.scorer.subtype_classifier:
                subtype_report = self.scorer.subtype_classifier.get_report(flat)
                logger.info(subtype_report)
        else:
            # Fall back to simple test type priority
            flat.sort(key=lambda x: PRIORITY.get(x.get("type", "UseCase"), 1), reverse=True)
        
        return flat

    def _compute_reward(
        self,
        result:  TestResult,
        action:  int,
        heur_conf: int,
        idx:     int,
        total:   int,
        report:  ExecutionReport,
        llm_forced_off: bool = False,
    ) -> float:
        reward = 0.0

        # LLM was the right call but all keys were quota-exhausted — don't
        # train on infrastructure failure; give neutral reward for this step.
        if llm_forced_off:
            return 0.0

        # ── Oracle efficiency rewards (the RL agent's actual job) ──────────
        # The agent is rewarded for choosing the RIGHT oracle for the situation,
        # NOT for whether tests pass or fail. Failures are GOOD — they are what
        # we are looking for. We never penalise finding bugs.

        if result.status in (TestStatus.PASSED, TestStatus.FAILED):
            # Clear outcome — we got a verifiable answer
            if action == 0:   # used heuristic
                if heur_conf >= 70:
                    reward += 2.0   # efficient: heuristic was confident enough
                else:
                    reward -= 1.0   # should have called LLM (uncertain result)
            elif action == 1:  # used LLM
                if heur_conf >= 70:
                    reward -= 2.0   # wasted LLM call — heuristic was fine
                else:
                    reward += 1.0   # LLM was genuinely needed
        elif result.status == TestStatus.ERROR:
            # Genuinely unclear outcome — neither oracle could determine result
            reward -= 1.0   # mild penalty (not -3; it may not be agent's fault)

        # Hard penalty only for actually exceeding budget
        if report.api_calls_used > self.api_budget:
            reward -= 50.0

        return reward

    # ── [RL Goal 1] Adaptive early-stop threshold ─────────────────────────

    def _compute_early_stop_threshold(self) -> int:
        """
        Return the uncertain-count threshold for early stopping.

        Uses the last 3 runs stored by RLPerformanceTracker:
        - Historically easy sites (avg pass ≥ 80 %) → threshold = 3 (stop sooner)
        - Historically hard sites (avg pass ≤ 40 %) → threshold = 8 (be more patient)
        - Unknown / mixed                           → threshold = 5 (default)
        """
        snapshots = self.perf_tracker.snapshots
        if len(snapshots) >= 3:
            avg_pass = sum(s.pass_rate for s in snapshots[-3:]) / 3
            if avg_pass >= 0.80:
                return 3
            elif avg_pass <= 0.40:
                return 8
        return 5

    # ── [RL Goal 2] Load persisted risk scores ────────────────────────────

    def _load_persisted_risk_scores(self) -> None:
        """
        Read the most-recent risk-score update per subtype from
        data/rl_optimizations/score_updates.jsonl and inject them into
        TestSubtypeClassifier.SUBTYPE_RISK so this run uses learned scores.

        Each line is a SubtypeScoreUpdate JSON record.  We keep the last
        value written per subtype (latest run wins).
        """
        if not _RL_OPT_SCORES_FILE.exists():
            return
        latest: Dict[str, float] = {}
        try:
            with open(_RL_OPT_SCORES_FILE, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    subtype      = rec.get("subtype")
                    updated_risk = rec.get("updated_risk")
                    if subtype and updated_risk is not None:
                        latest[subtype] = float(updated_risk)
        except Exception as exc:
            logger.warning(f"[RL Goal 2] Could not load persisted risk scores: {exc}")
            return

        applied = 0
        for subtype, risk in latest.items():
            if subtype in TestSubtypeClassifier.SUBTYPE_RISK:
                TestSubtypeClassifier.SUBTYPE_RISK[subtype] = risk
                applied += 1

        if applied:
            logger.info(
                f"[RL Goal 2] Applied {applied} persisted risk-score updates "
                f"from {_RL_OPT_SCORES_FILE}"
            )
