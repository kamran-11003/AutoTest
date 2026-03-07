"""Quick diagnostic: show RL learning state and per-run oracle decisions."""
import torch, json, glob
from pathlib import Path

# ── RL checkpoint ─────────────────────────────────────────────────────────────
ckpt_path = Path("data/rl_model/dqn_checkpoint.pth")
if ckpt_path.exists():
    ckpt = torch.load(ckpt_path, map_location="cpu")
    eps   = ckpt["epsilon"]
    steps = ckpt["steps"]
    print("=== RL Checkpoint ===")
    print(f"  Steps trained : {steps}")
    print(f"  Epsilon       : {eps:.4f}  (1.0=fully random  →  0.01=fully learned)")
    pct_random = round(eps * 100, 1)
    print(f"  Still random  : {pct_random}% of oracle choices are random exploration")
    if eps <= 0.05:
        print("  STATUS: RL fully converged — making deliberate oracle decisions")
    elif eps <= 0.15:
        print("  STATUS: RL mostly learned — mostly deliberate, some exploration")
    else:
        print("  STATUS: RL still learning — significant random exploration remains")
else:
    print("No RL checkpoint found at", ckpt_path)

# ── Run history ───────────────────────────────────────────────────────────────
reports = sorted(glob.glob("data/test_results/report_*.json"))
print(f"\n=== Run History ({len(reports)} runs) ===")
header = f"{'#':<4} {'Pass%':<8} {'LLM':<6} {'Heur':<6} {'LLM%':<8} {'API $':<8} Timestamp"
print(header)
print("-" * len(header))
for i, path in enumerate(reports, 1):
    d    = json.load(open(path, encoding="utf-8"))
    llm  = d.get("llm_decisions", 0)
    heur = d.get("heuristic_decisions", 0)
    pct  = round(100 * llm / (llm + heur), 1) if (llm + heur) else 0
    cost = d.get("api_cost_usd", 0)
    ts   = d.get("generated_at", "?")[:19]
    print(f"{i:<4} {d['pass_rate']:<8} {llm:<6} {heur:<6} {pct:<8} ${cost:<7.3f} {ts}")

print()
print("=== What RL decides ===")
print("  The RL agent does NOT skip tests — it runs ALL tests every time.")
print("  Its job is to choose, per-test, whether to use:")
print("    Action 0 = heuristic oracle (free, instant)")
print("    Action 1 = LLM oracle       ($0.002, slower, more accurate)")
print()
print("  Rewards:")
print("    +2 Heuristic used and was confident (>=70%) — good efficiency")
print("    +1 LLM used and heuristic was uncertain    — LLM was needed")
print("    -2 LLM used but heuristic was confident    — wasted API call")
print("    -1 Heuristic used but was uncertain        — should have called LLM")
print()
print("  PROOF IT IS LEARNING: as epsilon drops, LLM% should stabilise at the")
print("  minimum needed (only escalating genuinely ambiguous tests).")
print("  A fully converged agent uses LLM for ~5-15% of tests (1-4 per run of 25).")
