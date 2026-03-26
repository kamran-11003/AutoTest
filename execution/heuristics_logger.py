"""
Heuristics Logger - Tracks all 6 heuristic factors + RL learning per test.
Shows which factors drive prioritization and how agent learns from subtypes.
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class HeuristicFactors:
    """All 6 heuristic factors for a test"""
    test_id: str
    test_type: str
    subtype: str
    
    # 6 Factors (weights shown in comments)
    subtype_risk: float                     # 40% weight - most important
    input_complexity_risk: float            # Factor 2
    field_type_risk: float                  # Factor 3
    form_complexity_risk: float             # Factor 4
    validation_rules_risk: float            # Factor 5
    boundary_values_risk: float             # Factor 6
    
    final_failure_probability: float
    priority: int
    
    # Explanations
    factors_used: List[str]
    timestamp: str


class HeuristicsLogger:
    """Logs 6 heuristic factors + RL agent decisions per test subtype"""
    
    def __init__(self, output_dir: str = "data/heuristics_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.heuristics_file = self.output_dir / "heuristics_applied.jsonl"
        self.learning_file = self.output_dir / "subtype_learning.jsonl"
        self.report_file = self.output_dir / "heuristics_analysis.txt"
        
        self.heuristics_cache: Dict[str, HeuristicFactors] = {}
        self.subtype_stats: Dict[str, Dict] = {}
        self._load_existing()
    
    def _load_existing(self):
        """Load existing logs"""
        if self.heuristics_file.exists():
            try:
                with open(self.heuristics_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            h = HeuristicFactors(**data)
                            self.heuristics_cache[h.test_id] = h
            except Exception as e:
                logger.warning(f"Could not load heuristics: {e}")
        
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            subtype = record.get('subtype', 'unknown')
                            if subtype not in self.subtype_stats:
                                self.subtype_stats[subtype] = {
                                    'total': 0,
                                    'heuristic_passed': 0,
                                    'heuristic_failed': 0,
                                    'llm_passed': 0,
                                    'llm_failed': 0,
                                    'heuristic_reward': 0.0,
                                    'llm_reward': 0.0,
                                    'heuristic_uses': 0,
                                    'llm_uses': 0,
                                    'rewards': [],
                                }
                            
                            stats = self.subtype_stats[subtype]
                            stats['total'] += 1
                            stats['rewards'].append(record.get('reward', 0))
                            
                            if record.get('action') == 'heuristic':
                                stats['heuristic_uses'] += 1
                                stats['heuristic_reward'] += record.get('reward', 0)
                                if record.get('result') == 'PASSED':
                                    stats['heuristic_passed'] += 1
                                elif record.get('result') == 'FAILED':
                                    stats['heuristic_failed'] += 1
                            else:
                                stats['llm_uses'] += 1
                                stats['llm_reward'] += record.get('reward', 0)
                                if record.get('result') == 'PASSED':
                                    stats['llm_passed'] += 1
                                elif record.get('result') == 'FAILED':
                                    stats['llm_failed'] += 1
            except Exception as e:
                logger.warning(f"Could not load learning stats: {e}")
    
    def log_heuristics(
        self,
        test_id: str,
        test_type: str,
        subtype: str,
        subtype_risk: float,
        input_complexity_risk: float = 0.0,
        field_type_risk: float = 0.0,
        form_complexity_risk: float = 0.0,
        validation_rules_risk: float = 0.0,
        boundary_values_risk: float = 0.0,
        final_failure_probability: float = 0.0,
        priority: int = 0,
        factors_explanation: Optional[List[str]] = None,
    ):
        """Log all 6 heuristic factors applied to a test"""
        
        h = HeuristicFactors(
            test_id=test_id,
            test_type=test_type,
            subtype=subtype,
            subtype_risk=round(subtype_risk, 4),
            input_complexity_risk=round(input_complexity_risk, 4),
            field_type_risk=round(field_type_risk, 4),
            form_complexity_risk=round(form_complexity_risk, 4),
            validation_rules_risk=round(validation_rules_risk, 4),
            boundary_values_risk=round(boundary_values_risk, 4),
            final_failure_probability=round(final_failure_probability, 4),
            priority=priority,
            factors_used=factors_explanation or [],
            timestamp=datetime.now().isoformat(),
        )
        
        self.heuristics_cache[test_id] = h
        
        try:
            with open(self.heuristics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(h)) + '\n')
        except Exception as e:
            logger.error(f"Error logging heuristics: {e}")
    
    def log_rl_outcome(
        self,
        test_id: str,
        subtype: str,
        rl_action: int,  # 0=heuristic, 1=LLM
        result_status: str,  # PASSED/FAILED/ERROR
        reward: float,
    ):
        """Log RL agent's action and result per test subtype"""
        
        if subtype not in self.subtype_stats:
            self.subtype_stats[subtype] = {
                'total': 0,
                'heuristic_passed': 0,
                'heuristic_failed': 0,
                'llm_passed': 0,
                'llm_failed': 0,
                'heuristic_reward': 0.0,
                'llm_reward': 0.0,
                'heuristic_uses': 0,
                'llm_uses': 0,
                'rewards': [],
            }
        
        stats = self.subtype_stats[subtype]
        stats['total'] += 1
        stats['rewards'].append(reward)
        
        if rl_action == 0:  # Heuristic used
            stats['heuristic_uses'] += 1
            stats['heuristic_reward'] += reward
            if result_status == 'PASSED':
                stats['heuristic_passed'] += 1
            elif result_status == 'FAILED':
                stats['heuristic_failed'] += 1
        else:  # LLM used
            stats['llm_uses'] += 1
            stats['llm_reward'] += reward
            if result_status == 'PASSED':
                stats['llm_passed'] += 1
            elif result_status == 'FAILED':
                stats['llm_failed'] += 1
        
        # Save to file
        try:
            with open(self.learning_file, 'a', encoding='utf-8') as f:
                record = {
                    'subtype': subtype,
                    'test_id': test_id,
                    'action': 'heuristic' if rl_action == 0 else 'llm',
                    'result': result_status,
                    'reward': reward,
                    'timestamp': datetime.now().isoformat(),
                }
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            logger.error(f"Error logging outcome: {e}")
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        
        report = ["# HEURISTICS & RL LEARNING ANALYSIS\n"]
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        report.append(f"Total subtypes analyzed: {len(self.subtype_stats)}\n")
        
        if not self.subtype_stats:
            report.append("No learning data recorded yet.")
            return "\n".join(report)
        
        report.append("## Test Subtype Analysis\n")
        report.append("What did the agent LEARN about each test subtype?\n")
        
        report.append("### Legend:")
        report.append("- **Heuristic +2.0**: Agent correctly chose heuristic (confident test)")
        report.append("- **Heuristic -1.0**: Agent made wrong choice (should have used LLM)")
        report.append("- **LLM +1.0**: Agent correctly chose LLM (uncertain test needed expert)")
        report.append("- **LLM -2.0**: Agent made wrong choice (wasted API call, heuristic was fine)\n")
        
        for subtype in sorted(self.subtype_stats.keys()):
            stats = self.subtype_stats[subtype]
            total = stats['total']
            
            if total == 0:
                continue
            
            heur_uses = stats['heuristic_uses']
            llm_uses = stats['llm_uses']
            heur_pass = stats['heuristic_passed']
            llm_pass = stats['llm_passed']
            
            heur_pass_rate = heur_pass / heur_uses if heur_uses > 0 else 0
            llm_pass_rate = llm_pass / llm_uses if llm_uses > 0 else 0
            
            heur_avg_reward = stats['heuristic_reward'] / heur_uses if heur_uses > 0 else 0
            llm_avg_reward = stats['llm_reward'] / llm_uses if llm_uses > 0 else 0
            overall_avg = sum(stats['rewards']) / len(stats['rewards']) if stats['rewards'] else 0
            
            report.append(f"### {subtype.upper()}\n")
            report.append(f"**Execution Count:** {total} tests")
            report.append(f"- Heuristic: {heur_uses} uses ({heur_uses/total*100:.0f}%)")
            report.append(f"- LLM: {llm_uses} uses ({llm_uses/total*100:.0f}%)\n")
            
            report.append(f"**Success Rates:**")
            report.append(f"- Heuristic: {heur_pass}/{heur_uses} passed ({heur_pass_rate:.1%})")
            report.append(f"- LLM: {llm_pass}/{llm_uses} passed ({llm_pass_rate:.1%})\n")
            
            report.append(f"**Learning Signal (Rewards):**")
            report.append(f"- Heuristic avg: {heur_avg_reward:+.2f}")
            report.append(f"- LLM avg: {llm_avg_reward:+.2f}")
            report.append(f"- Overall: {overall_avg:+.2f}\n")
            
            # Agent's learning
            if heur_pass_rate > 0.80 and heur_avg_reward > 0.5:
                report.append(f"✅ **LEARNED:** Heuristic works great! ({heur_pass_rate:.0%} success)\n")
            elif llm_pass_rate > 0.80 and llm_avg_reward > 0.5:
                report.append(f"✅ **LEARNED:** Needs LLM expertise ({llm_pass_rate:.0%} success)\n")
            elif heur_avg_reward < -0.5 and llm_avg_reward > 0:
                report.append(f"⚠️ **LEARNED:** Heuristic often fails → Agent should use LLM more\n")
            else:
                report.append(f"🔄 **LEARNING:** Still optimizing oracle selection\n")
        
        report.append("\n## Factor Usage Distribution\n")
        report.append("Which heuristic factors are most important?\n")
        
        if self.heuristics_cache:
            factor_usage = {
                'subtype': 0,
                'input_complexity': 0,
                'field_type': 0,
                'form_complexity': 0,
                'validation_rules': 0,
                'boundary_values': 0,
            }
            
            for h in self.heuristics_cache.values():
                if h.subtype_risk > 0:
                    factor_usage['subtype'] += 1
                if h.input_complexity_risk > 0:
                    factor_usage['input_complexity'] += 1
                if h.field_type_risk > 0:
                    factor_usage['field_type'] += 1
                if h.form_complexity_risk > 0:
                    factor_usage['form_complexity'] += 1
                if h.validation_rules_risk > 0:
                    factor_usage['validation_rules'] += 1
                if h.boundary_values_risk > 0:
                    factor_usage['boundary_values'] += 1
            
            total_tests = len(self.heuristics_cache)
            report.append("| Factor | Used In | Frequency |")
            report.append("|--------|---------|-----------|")
            for factor, count in sorted(factor_usage.items(), key=lambda x: x[1], reverse=True):
                pct = count / total_tests * 100 if total_tests > 0 else 0
                report.append(f"| {factor.replace('_', ' ').title()} | {count} | {pct:.0f}% |")
        
        report.append("\n---")
        report.append("*Report generated by HeuristicsLogger*")
        
        return "\n".join(report)
    
    def save_analysis_report(self):
        """Generate and save analysis report"""
        report = self.generate_analysis_report()
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Heuristics analysis saved to {self.report_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total_tests = sum(s['total'] for s in self.subtype_stats.values())
        total_heur = sum(s['heuristic_uses'] for s in self.subtype_stats.values())
        total_llm = sum(s['llm_uses'] for s in self.subtype_stats.values())
        avg_reward = sum(sum(s['rewards']) for s in self.subtype_stats.values()) / total_tests if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'total_subtypes': len(self.subtype_stats),
            'heuristic_uses': total_heur,
            'llm_uses': total_llm,
            'heuristic_percentage': total_heur / total_tests * 100 if total_tests > 0 else 0,
            'llm_percentage': total_llm / total_tests * 100 if total_tests > 0 else 0,
            'average_reward': avg_reward,
        }
    
    def get_subtype_statistics(self) -> Dict[str, Dict]:
        """Get subtype statistics for heuristics optimizer"""
        return self.subtype_stats
