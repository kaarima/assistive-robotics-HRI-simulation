from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from attention_module import AttentionModule
from feedback import FeedbackSystem
from task_manager import Task, TaskManager
from utils import AttentionState, EpisodeStats, RateLimiter


@dataclass
class Decision:
    action: str  # "prompt_task", "wait", "encourage", "end"
    reason: str


class InteractionLoop:
    """
    Simulated HRI loop showing a clear robotics pattern:
      sense -> decide -> act
    """

    def __init__(
        self,
        attention: AttentionModule,
        tasks: TaskManager,
        feedback: FeedbackSystem,
        stats: EpisodeStats,
    ) -> None:
        self.attention = attention
        self.tasks = tasks
        self.feedback = feedback
        self.stats = stats
        self._limiter = RateLimiter(min_interval_s=0.6)
        self._current_task: Optional[Task] = None

    def close(self) -> None:
        self.attention.close()

    def run(self, max_tasks: int = 8) -> None:
        self._say("Hi! I’m your learning buddy robot. Let’s do a few short activities.")
        self._say("Tip: You can type 'quit' anytime.")

        while self.stats.tasks_attempted < max_tasks:
            self.stats.total_steps += 1

            # --- SENSE ---
            reading = self.attention.sense()

            # --- DECIDE ---
            decision = self._decide(reading.state)

            # --- ACT ---
            if decision.action == "end":
                break
            if decision.action == "wait":
                msg = self.feedback.on_attention(reading.state)
                if msg:
                    self._say(msg.text)
                continue

            if decision.action == "prompt_task":
                self._current_task = self.tasks.next_task()
                self._do_task(self._current_task)
                continue

        self._wrap_up()

    def _decide(self, attn: AttentionState) -> Decision:
        # If attention is absent, do not push tasks.
        if attn == AttentionState.ABSENT:
            return Decision(action="wait", reason="user_absent")

        # If distracted, we may still proceed but with short redirect.
        if attn == AttentionState.DISTRACTED:
            # If we just redirected recently, avoid spamming.
            if not self._limiter.ready():
                return Decision(action="wait", reason="rate_limit_redirect")
            return Decision(action="wait", reason="redirect_then_wait")

        # Attentive -> proceed to a task.
        return Decision(action="prompt_task", reason="attentive")

    def _do_task(self, task: Task) -> None:
        self.stats.tasks_attempted += 1

        self._say(f"\nTask #{task.id}  (difficulty {task.difficulty})")
        self._say(task.prompt)
        user = input("> ").strip()
        if user.lower() in {"quit", "exit"}:
            self.stats.tasks_attempted -= 1  # don't count this as a task attempt
            self._say("Okay—ending the session.")
            self._wrap_up()
            raise SystemExit(0)

        result = self.tasks.evaluate(task, user)
        success = bool(result.correct)

        # Update stats.
        self.stats.last_task_success = success
        if success:
            self.stats.tasks_completed += 1
            self.stats.consecutive_success += 1
            self.stats.consecutive_fail = 0
        else:
            self.stats.consecutive_fail += 1
            self.stats.consecutive_success = 0

        msg = self.feedback.on_result(success, self.stats)
        self._say(msg.text)

        # Adaptive behavior: adjust difficulty based on performance.
        self.tasks.adjust_difficulty(success=success)

        # If failed, offer a tiny hint (not too verbose).
        if not success and result.expected:
            self._say(f"Hint: expected was: {result.expected}")

    def _wrap_up(self) -> None:
        self._say("\nSession summary:")
        self._say(f"- Tasks attempted: {self.stats.tasks_attempted}")
        self._say(f"- Tasks completed: {self.stats.tasks_completed}")
        if self.stats.tasks_attempted > 0:
            rate = 100.0 * (self.stats.tasks_completed / float(self.stats.tasks_attempted))
            self._say(f"- Success rate: {rate:.1f}%")
        self._say("Thanks for working with me today.")

    def _say(self, text: str) -> None:
        print(f"[Robot] {text}")

