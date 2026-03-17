from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from utils import AttentionState, EpisodeStats, RNG


@dataclass
class FeedbackMessage:
    text: str
    tone: str  # "encourage", "neutral", "celebrate", "redirect"


class FeedbackSystem:
    """
    Generates short, supportive feedback messages.

    Note: This is a simulation; in real HRI you'd tailor language carefully,
    include caregiver controls, and validate against clinical guidelines.
    """

    def __init__(self, rng: RNG) -> None:
        self.rng = rng

    def on_attention(self, attn: AttentionState) -> Optional[FeedbackMessage]:
        if attn == AttentionState.ATTENTIVE:
            return None
        if attn == AttentionState.DISTRACTED:
            return FeedbackMessage(
                text=self.rng.choice(
                    [
                        "It’s okay—let’s take a breath and focus on the next step.",
                        "Let’s bring our attention back. You can do this.",
                        "Quick reset: look at the instruction, then try one step.",
                    ]
                ),
                tone="redirect",
            )
        return FeedbackMessage(
            text=self.rng.choice(
                [
                    "I’ll wait for you. When you’re ready, we’ll continue together.",
                    "No rush—come back when you’re ready and we’ll try again.",
                ]
            ),
            tone="redirect",
        )

    def on_result(self, success: bool, stats: EpisodeStats) -> FeedbackMessage:
        if success:
            if stats.consecutive_success >= 2:
                return FeedbackMessage(
                    text=self.rng.choice(
                        [
                            "Awesome streak! Let’s try a slightly bigger challenge.",
                            "Great job—you're getting really good at this!",
                            "Nice work! Ready for the next one?",
                        ]
                    ),
                    tone="celebrate",
                )
            return FeedbackMessage(
                text=self.rng.choice(
                    [
                        "Great job!",
                        "Nice! You got it.",
                        "Well done—keep going!",
                    ]
                ),
                tone="encourage",
            )

        # Failure
        if stats.consecutive_fail >= 2:
            return FeedbackMessage(
                text=self.rng.choice(
                    [
                        "That one was tricky. Let’s make it a bit easier and try again.",
                        "Good try. We’ll simplify it and go step-by-step.",
                        "No worries—let’s do a smaller version together.",
                    ]
                ),
                tone="encourage",
            )

        return FeedbackMessage(
            text=self.rng.choice(
                [
                    "Good try—let’s try once more.",
                    "Almost! Read the instruction one more time.",
                    "That’s okay. Try again—one step at a time.",
                ]
            ),
            tone="encourage",
        )

