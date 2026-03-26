"""
RL Heuristics Optimizer - Updates test risk scores based on RL agent learning.
Records initial heuristic scores and adjusts them based on actual test outcomes.
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class SubtypeScoreUpdate:
    """Track risk score changes for a test subtype"""
    subtype: str
    test_type: str
    
    # Before
    initial_risk: float
    initial_confidence: float
    
    # Execution stats
    total_tests: int
    heuristic_success_rate: float
    llm_success_rate: float
    heuristic_uses: int
    llm_uses: int
    avg_reward: float
    
    # After
    updated_risk: float
    risk_change: float
    confidence_change: float
    reason: str
    timestamp: str


class RLHeuristicsOptimizer:
    """Updates heuristic risk scores based on RL outcomes"""
    
    def __init__(self, output_dir: str = "data/rl_optimizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.updates_file = self.output_dir / "score_updates.jsonl"
        self.report_file = self.output_dir / "optimization_report.txt"
        
        self.initial_scores: Dict[str, Dict] = {}
        self.updates: List[SubtypeScoreUpdate] = []
    
    def record_initial_scores(
        self,
        subtype: str,
        test_type: str,
        initial_risk: float,
        initial_confidence: float,
    ):
        """Record pre-execution risk scores"""
        self.initial_scores[subtype] = {
            'test_type': test_type,
            'risk': initial_risk,
            'confidence': initial_confidence,
        }
    
    def compute_updates(self, subtype_stats: Dict[str, Dict]) -> List[SubtypeScoreUpdate]:
        """Compute new risk scores based on execution outcomes"""
        
        updates = []
        
        for subtype, stats in subtype_stats.items():
            if subtype not in self.initial_scores:
                continue
            
            initial = self.initial_scores[subtype]
            total = stats['total']
            if total == 0:
                continue
            
            heur_uses = stats['heuristic_uses']
            llm_uses = stats['llm_uses']
            heur_success = stats['heuristic_passed'] / heur_uses if heur_uses > 0 else 0
            llm_success = stats['llm_passed'] / llm_uses if llm_uses > 0 else 0
            avg_reward = sum(stats['rewards']) / len(stats['rewards']) if stats['rewards'] else 0
            
            # Compute new risk
            new_risk, reason, conf_delta = self._compute_new_risk(
                initial_risk=initial['risk'],
                heur_success=heur_success,
                llm_success=llm_success,
                heur_uses=heur_uses,
                llm_uses=llm_uses,
                avg_reward=avg_reward,
            )
            
            update = SubtypeScoreUpdate(
                subtype=subtype,
                test_type=initial['test_type'],
                initial_risk=round(initial['risk'], 4),
                initial_confidence=round(initial['confidence'], 4),
                total_tests=total,
                heuristic_success_rate=round(heur_success, 4),
                llm_success_rate=round(llm_success, 4),
                heuristic_uses=heur_uses,
                llm_uses=llm_uses,
                avg_reward=round(avg_reward, 4),
                updated_risk=round(new_risk, 4),
                risk_change=round(new_risk - initial['risk'], 4),
                confidence_change=round(conf_delta, 4),
                reason=reason,
                timestamp=datetime.now().isoformat(),
            )
            
            updates.append(update)
        
        self.updates = updates
        self._save_updates()
        
        return updates
    
    def _compute_new_risk(
        self,
        initial_risk: float,
        heur_success: float,
        llm_success: float,
        heur_uses: int,
        llm_uses: int,
        avg_reward: float,
    ) -> Tuple[float, str, float]:
        """Calculate updated risk based on what RL learned"""
        
        # If LLM much better than heuristic → test IS harder than we thought
        if llm_success > heur_success + 0.2 and llm_uses > 0:
            increase = 0.05 + (llm_success - heur_success) * 0.1
            new_risk = min(1.0, initial_risk + increase)
            reason = f"LLM {llm_success:.0%} >> Heuristic {heur_success:.0%} → Test harder"
            conf_delta = 0.05
        
        # If heuristic works great (>85%) → test IS easier than we thought
        elif heur_success > 0.85 and heur_uses > 2:
            decrease = min(0.05, initial_risk * 0.1)
            new_risk = max(0.0, initial_risk - decrease)
            reason = f"Heuristic {heur_success:.0%} success → Test easier than expected"
            conf_delta = -0.05
        
        # If RL agent learning well (positive rewards) → keep high risk
        elif avg_reward > 0.5 and llm_uses > heur_uses:
            new_risk = min(1.0, initial_risk + 0.02)
            reason = f"RL reward {avg_reward:+.2f} → Test needs LLM"
            conf_delta = 0.03
        
        # If RL agent struggling (negative rewards) → lower risk
        elif avg_reward < -0.5:
            new_risk = max(0.0, initial_risk - 0.03)
            reason = f"RL reward {avg_reward:+.2f} → Test less risky"
            conf_delta = -0.05
        
        else:
            new_risk = initial_risk
            reason = f"Balanced execution"
            conf_delta = 0.0
        
        return new_risk, reason, conf_delta
    
    def _save_updates(self):
        """Save to JSONL"""
        try:
            with open(self.updates_file, 'a', encoding='utf-8') as f:
                for update in self.updates:
                    f.write(json.dumps(asdict(update)) + '\n')
        except Exception as e:
            logger.error(f"Error saving updates: {e}")
    
    def generate_report(self) -> str:
        """Generate optimization report"""
        
        report = ["# RL HEURISTICS OPTIMIZATION REPORT\n"]
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        
        if not self.updates:
            report.append("No updates yet.")
            return "\n".join(report)
        
        report.append("## Risk Score Changes: Before vs After RL Learning\n\n")
        report.append("| Subtype | Before | After | Change | Reason |")
        report.append("|---------|--------|-------|--------|--------|")
        
        for u in sorted(self.updates, key=lambda x: abs(x.risk_change), reverse=True):
            emoji = "🔺" if u.risk_change > 0 else "🔻" if u.risk_change < 0 else "→"
            report.append(
                f"| {u.subtype:<30} | {u.initial_risk:.3f} | {u.updated_risk:.3f} | "
                f"{emoji} {u.risk_change:+.4f} | {u.reason[:40]} |"
            )
        
        report.append("\n## Detailed Analysis Per Subtype\n")
        
        for u in self.updates:
            report.append(f"\n### {u.subtype}\n")
            report.append(f"**Before:** Risk = {u.initial_risk:.3f}")
            report.append(f"**After:** Risk = {u.updated_risk:.3f}")
            report.append(f"**Change:** {u.risk_change:+.4f}\n")
            
            report.append(f"**What Happened During Execution:**")
            report.append(f"- Total tests: {u.total_tests}")
            report.append(f"- Heuristic: {u.heuristic_uses} uses → {u.heuristic_success_rate:.0%} success")
            report.append(f"- LLM: {u.llm_uses} uses → {u.llm_success_rate:.0%} success")
            report.append(f"- RL learning signal: {u.avg_reward:+.2f}\n")
            
            report.append(f"**Why Risk Changed:**")
            report.append(f"- {u.reason}\n")
        
        report.append("---")
        report.append("\n**Impact:** These updated scores will be used in the NEXT test execution cycle.")
        report.append("The RL agent continuously improves its test prioritization strategy.\n")
        report.append("*Report generated by RLHeuristicsOptimizer*")
        
        return "\n".join(report)
    
    def save_report(self):
        """Save human-readable report"""
        report = self.generate_report()
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Optimization report: {self.report_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get summary statistics"""
        if not self.updates:
            return {}
        
        risk_increases = sum(1 for u in self.updates if u.risk_change > 0)
        risk_decreases = sum(1 for u in self.updates if u.risk_change < 0)
        avg_change = sum(u.risk_change for u in self.updates) / len(self.updates)
        
        return {
            'total_subtypes_optimized': len(self.updates),
            'risk_increases': risk_increases,
            'risk_decreases': risk_decreases,
            'average_risk_change': avg_change,
            'largest_increase': max((u.risk_change for u in self.updates), default=0),
            'largest_decrease': min((u.risk_change for u in self.updates), default=0),
        }
