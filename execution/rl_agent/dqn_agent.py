"""
DQN Reinforcement Learning Agent

The agent decides per-test HOW to verify the outcome:
  Action 0 → trust the heuristic oracle (free)
  Action 1 → escalate to the LLM oracle  ($0.002)

IMPORTANT: The neural net NEVER decides to stop.
Stopping is handled by hard rules in AdaptiveRunner:
  - API budget exhausted
  - Time limit reached
  - Oracle confidence consistently < 50 for last 5 tests
This separation keeps the net's job simple and prevents the
common RL failure mode of stopping early to avoid uncertainty.

State vector (10 features, see build_state()):
  0  tests_run / total
  1  failures / max(tests_run, 1)
  2  consecutive_passes / 10  (normalised)
  3  avg_llm_confidence / 100
  4  uncertain_ratio  (unclear outcomes / tests so far)
  5  api_calls_used / api_budget
  6  time_elapsed / time_limit
  7  priority_encoded  (BVA=1.0 … UseCase=0.2)
  8  type_encoded
  9  num_inputs / 20  (normalised)

Reward function (oracle efficiency only — NOT pass/fail):
  +2   heuristic used AND confidence ≥ 70  (efficient)
  +1   LLM used AND confidence < 70 before (needed)
  -1   LLM used AND heuristic conf ≥ 70   (wasted call)
  -0.5 heuristic used AND confidence < 70 (should have used LLM)
  -50  budget exceeded
"""

import sys
import random
from pathlib import Path
from collections import deque
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.optim as optim

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

STATE_DIM  = 10
ACTION_DIM = 2  # 0=heuristic, 1=llm  (stop is a hard rule, never neural-net)
CKPT_PATH  = Path("data/rl_model/dqn_checkpoint.pth")


# ── Neural Network ─────────────────────────────────────────────────────────────

class DQNNetwork(nn.Module):
    def __init__(self, state_dim: int = STATE_DIM, action_dim: int = ACTION_DIM):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ── DQN Agent ─────────────────────────────────────────────────────────────────

class DQNAgent:
    def __init__(
        self,
        gamma:        float = 0.95,
        epsilon:      float = 1.0,
        epsilon_min:  float = 0.01,
        epsilon_decay: float = 0.995,
        lr:           float = 1e-3,
        batch_size:   int   = 32,
        memory_size:  int   = 2000,
    ):
        self.gamma         = gamma
        self.discount_factor = gamma   # alias used by performance tracker
        self.epsilon       = epsilon
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = lr        # alias used by performance tracker
        self.batch_size    = batch_size

        self.device = torch.device("cpu")   # keep lightweight for FYP
        self.model  = DQNNetwork().to(self.device)
        self.target = DQNNetwork().to(self.device)
        self.target.load_state_dict(self.model.state_dict())

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn   = nn.MSELoss()
        self.memory: deque = deque(maxlen=memory_size)

        self.steps = 0
        self.target_update_freq = 50   # sync target net every N steps

        # Always regenerate from scratch if checkpoint has 3 actions (old
        # format) or if checkpoint is missing.
        _load_ok = False
        if CKPT_PATH.exists():
            try:
                ckpt = torch.load(CKPT_PATH, map_location=self.device)
                # Check output layer size matches current ACTION_DIM=2
                saved_out = list(ckpt["model"].keys())[-1]   # last weight key
                saved_dim = ckpt["model"][saved_out].shape[0]
                if saved_dim == ACTION_DIM:
                    self.model.load_state_dict(ckpt["model"])
                    self.target.load_state_dict(ckpt["target"])
                    self.epsilon = ckpt.get("epsilon", 0.25)
                    self.steps   = ckpt.get("steps", 0)
                    logger.info(f"RL model loaded (ε={self.epsilon:.3f})")
                    _load_ok = True
                else:
                    logger.info(f"Old checkpoint has {saved_dim} actions — "
                                f"discarding and retraining.")
                    CKPT_PATH.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Checkpoint load failed: {e} — retraining.")
                CKPT_PATH.unlink(missing_ok=True)
        if not _load_ok:
            self._synthetic_pretraining()
            self.epsilon = 0.25   # modest exploration after bootstrap

    # ── Action selection ───────────────────────────────────────────────────

    def choose_action(self, state: List[float]) -> int:
        """Epsilon-greedy action selection. Returns 0 (heuristic) or 1 (LLM)."""
        if random.random() < self.epsilon:
            return random.randint(0, 1)   # only 0 or 1
        s = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(s)
        return int(q_values.argmax().item())  # 0 or 1

    # ── Memory & replay ────────────────────────────────────────────────────

    def remember(
        self,
        state:      List[float],
        action:     int,
        reward:     float,
        next_state: List[float],
        done:       bool,
    ):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        """Sample a mini-batch and train."""
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        s  = torch.FloatTensor(states).to(self.device)
        a  = torch.LongTensor(actions).to(self.device)
        r  = torch.FloatTensor(rewards).to(self.device)
        ns = torch.FloatTensor(next_states).to(self.device)
        d  = torch.FloatTensor(dones).to(self.device)

        q_current  = self.model(s).gather(1, a.unsqueeze(1)).squeeze(1)
        q_next_max = self.target(ns).max(1)[0].detach()
        q_target   = r + self.gamma * q_next_max * (1 - d)

        loss = self.loss_fn(q_current, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Periodically sync target network
        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.target.load_state_dict(self.model.state_dict())

    # ── Save / Load ────────────────────────────────────────────────────────

    def save(self):
        CKPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model":   self.model.state_dict(),
            "target":  self.target.state_dict(),
            "epsilon": self.epsilon,
            "steps":   self.steps,
        }, CKPT_PATH)
        logger.info(f"RL model saved → {CKPT_PATH}")

    def load(self):
        ckpt = torch.load(CKPT_PATH, map_location=self.device)
        self.model.load_state_dict(ckpt["model"])
        self.target.load_state_dict(ckpt["target"])
        self.epsilon = ckpt.get("epsilon", self.epsilon_min)
        self.steps   = ckpt.get("steps",   0)
        logger.info(f"RL model loaded from {CKPT_PATH} (ε={self.epsilon:.3f})")

    # ── Synthetic pre-training ─────────────────────────────────────────────

    def _synthetic_pretraining(self, n: int = 500):
        """
        Bootstrap the agent with 500 hand-crafted experience tuples so it
        doesn't start completely random on the first real run.

        Policy distilled from DemoQA crawl observations:
          - High budget remaining + uncertain heuristic → call LLM (action 1)
          - Many consecutive passes + budget low       → stop early (action 2)
          - High confidence heuristic                  → trust it (action 0)
        """
        logger.info("Generating 500 synthetic RL training experiences …")
        for _ in range(n):
            # Random plausible state
            tests_ratio       = random.uniform(0.0, 1.0)
            failure_ratio     = random.uniform(0.0, 0.5)
            consec_passes     = random.uniform(0.0, 1.0)
            avg_conf          = random.uniform(0.0, 1.0)
            uncertain_ratio   = random.uniform(0.0, 1.0)
            budget_used_ratio = random.uniform(0.0, 1.0)
            time_ratio        = random.uniform(0.0, 1.0)
            priority_enc      = random.uniform(0.0, 1.0)
            type_enc          = random.uniform(0.0, 1.0)
            num_inputs_norm   = random.uniform(0.0, 1.0)

            state = [tests_ratio, failure_ratio, consec_passes, avg_conf,
                     uncertain_ratio, budget_used_ratio, time_ratio,
                     priority_enc, type_enc, num_inputs_norm]

            # Expert policy for bootstrapping (only 0=heuristic or 1=LLM):
            # LLM when confidence is low and budget is available
            # Heuristic when confidence is high (most common case)
            if avg_conf < 0.6 and budget_used_ratio < 0.6:
                action, reward = 1, 2.0   # call LLM: heuristic uncertain
            elif avg_conf >= 0.7:
                action, reward = 0, 2.0   # trust heuristic: it's confident
            else:
                action, reward = 0, 1.0   # trust heuristic: borderline

            next_state = [min(1.0, tests_ratio + 0.05)] + state[1:]
            done = tests_ratio > 0.95

            self.remember(state, action, reward, next_state, done)

        # Train on the synthetic batch
        for _ in range(20):
            self.replay()

        self.save()
        logger.info("Synthetic pre-training complete, model saved.")

    # ── State builder helper ───────────────────────────────────────────────

    @staticmethod
    def build_state(
        tests_run:        int,
        total_tests:      int,
        failures:         int,
        consecutive_passes: int,
        avg_llm_confidence: float,
        uncertain_count:  int,
        api_calls_used:   int,
        api_budget:       int,
        time_elapsed_s:   float,
        time_limit_s:     float,
        test_case:        dict,
    ) -> List[float]:
        """Convert execution context into the 10-dimensional state vector."""
        type_map = {"BVA": 0.0, "ECP": 0.2, "StateTransition": 0.4,
                    "DecisionTable": 0.6, "UseCase": 0.8}
        priority_map = {"BVA": 1.0, "ECP": 0.8, "StateTransition": 0.6,
                        "DecisionTable": 0.4, "UseCase": 0.2}
        t = test_case.get("type", "BVA")

        safe_total  = max(total_tests, 1)
        safe_run    = max(tests_run, 1)
        safe_budget = max(api_budget, 1)
        safe_time   = max(time_limit_s, 1)

        return [
            tests_run / safe_total,
            failures  / safe_run,
            min(consecutive_passes / 10.0, 1.0),
            avg_llm_confidence / 100.0,
            uncertain_count / safe_run,
            api_calls_used  / safe_budget,
            time_elapsed_s  / safe_time,
            priority_map.get(t, 0.5),
            type_map.get(t, 0.0),
            min(len(test_case.get("test_data", {})) / 20.0, 1.0),
        ]
