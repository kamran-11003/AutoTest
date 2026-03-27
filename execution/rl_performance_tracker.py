"""
RL Performance Tracker - Monitors and logs RL agent learning metrics across test execution cycles.
Tracks epsilon decay, decision patterns, API costs, and performance trends.
"""

import json
import csv
import os
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class FactorChange:
    """Records a factor adjustment and reasoning."""
    factor_name: str
    old_value: Any
    new_value: Any
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RLPerformanceSnapshot:
    """Single execution snapshot with all relevant metrics."""
    run_number: int
    timestamp: str
    pass_rate: float  # 0-1
    heuristic_decisions: int
    llm_decisions: int
    llm_percentage: float  # 0-100
    api_calls_used: int
    api_cost: float
    execution_time_seconds: float
    epsilon: float  # RL exploration rate
    q_learning_rate: float
    discount_factor: float
    factor_changes: List[FactorChange] = field(default_factory=list)
    notes: str = ""


class RLPerformanceTracker:
    """
    Tracks RL agent learning metrics and performance across multiple test execution runs.
    Generates CSV, JSONL, and markdown reports for analysis.
    """

    def __init__(self, output_dir: str = "data/rl_performance"):
        """
        Initialize tracker with output directory.
        
        Args:
            output_dir: Directory to store performance logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.output_dir / "rl_performance.csv"
        self.jsonl_file = self.output_dir / "rl_performance.jsonl"
        self.changes_file = self.output_dir / "factor_changes.jsonl"
        self.summary_file = self.output_dir / "performance_summary.md"
        
        self.snapshots: List[RLPerformanceSnapshot] = []
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing snapshots from JSONL file if it exists."""
        if self.jsonl_file.exists():
            try:
                with open(self.jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            # Reconstruct FactorChange objects
                            factor_changes = [
                                FactorChange(**fc) if isinstance(fc, dict) else fc
                                for fc in data.get('factor_changes', [])
                            ]
                            data['factor_changes'] = factor_changes
                            snapshot = RLPerformanceSnapshot(**data)
                            self.snapshots.append(snapshot)
            except Exception as e:
                print(f"Warning: Failed to load existing performance data: {e}")

    def record_execution(
        self,
        pass_rate: float,
        heuristic_decisions: int,
        llm_decisions: int,
        api_calls_used: int,
        api_cost: float,
        execution_time_seconds: float,
        epsilon: float,
        q_learning_rate: float,
        discount_factor: float,
        factor_changes: Optional[List[Dict[str, Any]]] = None,
        notes: str = ""
    ) -> RLPerformanceSnapshot:
        """
        Record a single test execution with all relevant metrics.
        
        Args:
            pass_rate: Percentage of tests that passed (0-1)
            heuristic_decisions: Number of tests decided by heuristic
            llm_decisions: Number of tests decided by LLM
            api_calls_used: Number of API calls made in this run
            api_cost: Total cost of API calls in USD
            execution_time_seconds: Total execution time in seconds
            epsilon: Current RL exploration rate
            q_learning_rate: Current Q-learning rate
            discount_factor: RL discount factor
            factor_changes: List of factor changes applied
            notes: Human-readable notes about this run
            
        Returns:
            RLPerformanceSnapshot: The recorded snapshot
        """
        run_number = len(self.snapshots) + 1
        timestamp = datetime.now().isoformat()
        
        total_decisions = heuristic_decisions + llm_decisions
        llm_percentage = (llm_decisions / total_decisions * 100) if total_decisions > 0 else 0
        
        # Process factor changes
        changes = []
        if factor_changes:
            for change in factor_changes:
                fc = FactorChange(**change) if isinstance(change, dict) else change
                changes.append(fc)
        
        snapshot = RLPerformanceSnapshot(
            run_number=run_number,
            timestamp=timestamp,
            pass_rate=pass_rate,
            heuristic_decisions=heuristic_decisions,
            llm_decisions=llm_decisions,
            llm_percentage=llm_percentage,
            api_calls_used=api_calls_used,
            api_cost=api_cost,
            execution_time_seconds=execution_time_seconds,
            epsilon=epsilon,
            q_learning_rate=q_learning_rate,
            discount_factor=discount_factor,
            factor_changes=changes,
            notes=notes
        )
        
        self.snapshots.append(snapshot)
        self._append_to_jsonl(snapshot)
        self._append_to_csv(snapshot)
        self._append_factor_changes(snapshot)
        
        return snapshot

    def _append_to_jsonl(self, snapshot: RLPerformanceSnapshot):
        """Append snapshot to JSONL file."""
        try:
            with open(self.jsonl_file, 'a', encoding='utf-8') as f:
                # Convert factor changes to dicts for JSON serialization
                data = asdict(snapshot)
                data['factor_changes'] = [asdict(fc) for fc in snapshot.factor_changes]
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error writing to JSONL: {e}")

    def _append_to_csv(self, snapshot: RLPerformanceSnapshot):
        """Append snapshot to CSV file."""
        try:
            file_exists = self.csv_file.exists()
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'run_number', 'timestamp', 'pass_rate', 'heuristic_decisions',
                    'llm_decisions', 'llm_percentage', 'api_calls_used', 'api_cost',
                    'execution_time_seconds', 'epsilon', 'q_learning_rate',
                    'discount_factor', 'notes'
                ])
                if not file_exists:
                    writer.writeheader()
                
                row = {
                    'run_number': snapshot.run_number,
                    'timestamp': snapshot.timestamp,
                    'pass_rate': f"{snapshot.pass_rate:.2%}",
                    'heuristic_decisions': snapshot.heuristic_decisions,
                    'llm_decisions': snapshot.llm_decisions,
                    'llm_percentage': f"{snapshot.llm_percentage:.1f}%",
                    'api_calls_used': snapshot.api_calls_used,
                    'api_cost': f"${snapshot.api_cost:.4f}",
                    'execution_time_seconds': f"{snapshot.execution_time_seconds:.2f}",
                    'epsilon': f"{snapshot.epsilon:.6f}",
                    'q_learning_rate': f"{snapshot.q_learning_rate:.6f}",
                    'discount_factor': f"{snapshot.discount_factor:.4f}",
                    'notes': snapshot.notes
                }
                writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def _append_factor_changes(self, snapshot: RLPerformanceSnapshot):
        """Append factor changes to separate JSONL file."""
        if not snapshot.factor_changes:
            return
        
        try:
            with open(self.changes_file, 'a', encoding='utf-8') as f:
                for change in snapshot.factor_changes:
                    record = {
                        'run_number': snapshot.run_number,
                        'timestamp': snapshot.timestamp,
                        'factor_name': change.factor_name,
                        'old_value': str(change.old_value),
                        'new_value': str(change.new_value),
                        'reason': change.reason,
                        'change_timestamp': change.timestamp
                    }
                    f.write(json.dumps(record) + '\n')
        except Exception as e:
            print(f"Error writing factor changes: {e}")

    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive markdown report of performance trends.
        
        Returns:
            str: Markdown formatted report
        """
        if not self.snapshots:
            return "# RL Performance Report\n\nNo data recorded yet.\n"
        
        report = ["# RL Performance Report"]
        report.append(f"\n**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Total Runs:** {len(self.snapshots)}\n")
        
        # Summary statistics
        report.append("## Summary Statistics")
        latest = self.snapshots[-1]
        avg_pass_rate = sum(s.pass_rate for s in self.snapshots) / len(self.snapshots)
        avg_llm_pct = sum(s.llm_percentage for s in self.snapshots) / len(self.snapshots)
        total_cost = sum(s.api_cost for s in self.snapshots)
        
        report.append(f"- **Latest Pass Rate:** {latest.pass_rate:.2%}")
        report.append(f"- **Average Pass Rate:** {avg_pass_rate:.2%}")
        report.append(f"- **Latest LLM Usage:** {latest.llm_percentage:.1f}%")
        report.append(f"- **Average LLM Usage:** {avg_llm_pct:.1f}%")
        report.append(f"- **Total API Cost:** ${total_cost:.4f}")
        report.append(f"- **Current Epsilon:** {latest.epsilon:.6f}\n")
        
        # Trend analysis
        report.append("## Performance Trends")
        if len(self.snapshots) > 1:
            first = self.snapshots[0]
            pass_rate_change = (latest.pass_rate - first.pass_rate) * 100
            llm_change = latest.llm_percentage - first.llm_percentage
            
            report.append(f"- **Pass Rate Trend:** {pass_rate_change:+.1f}% (from {first.pass_rate:.2%} to {latest.pass_rate:.2%})")
            report.append(f"- **LLM Usage Trend:** {llm_change:+.1f}pp (from {first.llm_percentage:.1f}% to {latest.llm_percentage:.1f}%)")
            report.append(f"- **Optimizations:** {len([s for s in self.snapshots if s.factor_changes])} runs with adjustments\n")
        
        # Recent runs table
        report.append("## Recent Runs (Last 10)")
        report.append("| Run | Pass Rate | LLM % | API Cost | Epsilon | Time (s) |")
        report.append("|-----|-----------|-------|----------|---------|----------|")
        
        for snapshot in self.snapshots[-10:]:
            report.append(
                f"| {snapshot.run_number} | {snapshot.pass_rate:.2%} | "
                f"{snapshot.llm_percentage:.1f}% | ${snapshot.api_cost:.4f} | "
                f"{snapshot.epsilon:.6f} | {snapshot.execution_time_seconds:.1f} |"
            )
        
        report.append("")
        
        # Factor changes summary
        all_changes = [c for s in self.snapshots for c in s.factor_changes]
        if all_changes:
            report.append("## Factor Adjustments")
            report.append(f"**Total Adjustments:** {len(all_changes)}\n")
            
            # Group by factor
            by_factor = {}
            for change in all_changes:
                if change.factor_name not in by_factor:
                    by_factor[change.factor_name] = []
                by_factor[change.factor_name].append(change)
            
            for factor_name, changes in by_factor.items():
                report.append(f"### {factor_name} ({len(changes)} changes)")
                for change in changes[-3:]:  # Last 3 changes
                    report.append(f"- Run {self.snapshots[0].run_number if changes else '?'}: {change.old_value} → {change.new_value}")
                    report.append(f"  Reason: {change.reason}")
                report.append("")
        
        report.append("---")
        report.append("*Performance tracking with RLPerformanceTracker*")
        
        return "\n".join(report)

    def save_summary_report(self):
        """Generate and save the summary report to markdown file."""
        report = self.generate_summary_report()
        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f"Error saving summary report: {e}")
            return False

    def get_latest_snapshot(self) -> Optional[RLPerformanceSnapshot]:
        """Get the most recent performance snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def get_snapshots(self, limit: int = 10) -> List[RLPerformanceSnapshot]:
        """Get last N snapshots."""
        return self.snapshots[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics across all runs."""
        if not self.snapshots:
            return {}
        
        return {
            'total_runs': len(self.snapshots),
            'avg_pass_rate': sum(s.pass_rate for s in self.snapshots) / len(self.snapshots),
            'max_pass_rate': max(s.pass_rate for s in self.snapshots),
            'min_pass_rate': min(s.pass_rate for s in self.snapshots),
            'avg_llm_percentage': sum(s.llm_percentage for s in self.snapshots) / len(self.snapshots),
            'total_api_cost': sum(s.api_cost for s in self.snapshots),
            'total_execution_time': sum(s.execution_time_seconds for s in self.snapshots),
            'current_epsilon': self.snapshots[-1].epsilon,
            'epsilon_decay': self.snapshots[0].epsilon - self.snapshots[-1].epsilon if len(self.snapshots) > 1 else 0,
        }


# Example usage
if __name__ == "__main__":
    # Initialize tracker
    tracker = RLPerformanceTracker()
    
    # Example: Record a test execution
    snapshot = tracker.record_execution(
        pass_rate=0.85,
        heuristic_decisions=15,
        llm_decisions=10,
        api_calls_used=10,
        api_cost=0.02,
        execution_time_seconds=45.5,
        epsilon=0.1,
        q_learning_rate=0.001,
        discount_factor=0.99,
        factor_changes=[
            {
                'factor_name': 'epsilon',
                'old_value': 0.2,
                'new_value': 0.1,
                'reason': 'Decay schedule reached target exploration level'
            }
        ],
        notes="Optimized oracle selection reduced API calls by 30%"
    )
    
    print(f"Recorded execution run #{snapshot.run_number}")
    print(f"Pass rate: {snapshot.pass_rate:.2%}")
    print(f"LLM usage: {snapshot.llm_percentage:.1f}%")
    
    # Generate report
    tracker.save_summary_report()
    print(f"\nReport saved to {tracker.summary_file}")
