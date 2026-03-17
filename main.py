from __future__ import annotations

import argparse

from attention_module import AttentionModule
from feedback import FeedbackSystem
from interaction import InteractionLoop
from task_manager import TaskManager
from utils import EpisodeStats, RNG


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Assistive + Educational Robotics Simulation (ADHD/ASD)")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--tasks", type=int, default=8, help="Max tasks in a session")
    p.add_argument("--use-opencv", action="store_true", help="Use webcam face presence as attention proxy (if available)")
    p.add_argument("--min-difficulty", type=int, default=1)
    p.add_argument("--max-difficulty", type=int, default=6)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    rng = RNG(seed=args.seed)
    stats = EpisodeStats()

    attention = AttentionModule(rng=rng, use_opencv=args.use_opencv)
    tasks = TaskManager(rng=rng, min_difficulty=args.min_difficulty, max_difficulty=args.max_difficulty)
    feedback = FeedbackSystem(rng=rng)

    loop = InteractionLoop(attention=attention, tasks=tasks, feedback=feedback, stats=stats)
    try:
        loop.run(max_tasks=args.tasks)
    finally:
        loop.close()


if __name__ == "__main__":
    main()

