"""
Test Result Data Structures
Foundation dataclasses used by every other module in the execution layer.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    PASSED  = "passed"
    FAILED  = "failed"
    ERROR   = "error"
    SKIPPED = "skipped"


class OracleMethod(str, Enum):
    HEURISTIC = "heuristic"
    LLM       = "llm"
    NONE      = "none"


@dataclass
class TestResult:
    """Result of executing a single test case."""
    test_id:         str
    status:          TestStatus
    duration_ms:     float
    oracle_method:   OracleMethod = OracleMethod.HEURISTIC
    confidence:      int = 0          # 0-100
    evidence:        str = ""
    screenshot_path: Optional[str] = None
    error_message:   Optional[str] = None
    test_type:       str = ""         # BVA / ECP / StateTransition / …
    form_url:        str = ""
    test_value:      str = ""
    expected_result: str = ""
    timestamp:       str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "test_id":         self.test_id,
            "status":          self.status.value,
            "duration_ms":     round(self.duration_ms, 1),
            "oracle_method":   self.oracle_method.value,
            "confidence":      self.confidence,
            "evidence":        self.evidence,
            "screenshot_path": self.screenshot_path,
            "error_message":   self.error_message,
            "test_type":       self.test_type,
            "form_url":        self.form_url,
            "test_value":      str(self.test_value),
            "expected_result": self.expected_result,
            "timestamp":       self.timestamp,
        }


@dataclass
class ExecutionReport:
    """Aggregated report for a full test-suite execution run."""
    crawl_id:      str
    total:         int = 0
    passed:        int = 0
    failed:        int = 0
    errors:        int = 0
    skipped:       int = 0
    duration_s:    float = 0.0
    api_calls_used: int = 0
    api_cost:      float = 0.0        # USD estimate ($0.002 per LLM call)
    stop_reason:   str = "completed"  # completed | budget_exhausted | time_limit | rl_stop
    rl_mode:       bool = True
    results:       List[TestResult] = field(default_factory=list)
    generated_at:  str = field(default_factory=lambda: datetime.now().isoformat())

    # RL decision breakdown
    heuristic_decisions: int = 0
    llm_decisions:       int = 0
    stop_decisions:      int = 0
    pattern_overrides:   int = 0   # times pattern learning overrode DQN action

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.passed / self.total) * 100, 1)

    @property
    def failure_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.failed / self.total) * 100, 1)

    def to_dict(self) -> dict:
        return {
            "crawl_id":            self.crawl_id,
            "total":               self.total,
            "passed":              self.passed,
            "failed":              self.failed,
            "errors":              self.errors,
            "skipped":             self.skipped,
            "pass_rate":           self.pass_rate,
            "failure_rate":        self.failure_rate,
            "duration_s":          round(self.duration_s, 2),
            "api_calls_used":      self.api_calls_used,
            "api_cost_usd":        round(self.api_cost, 4),
            "stop_reason":         self.stop_reason,
            "rl_mode":             self.rl_mode,
            "heuristic_decisions": self.heuristic_decisions,
            "llm_decisions":       self.llm_decisions,
            "stop_decisions":      self.stop_decisions,
            "generated_at":        self.generated_at,
            "results":             [r.to_dict() for r in self.results],
        }
