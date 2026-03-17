from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol

from utils import RNG


class TaskType(str, Enum):
    SEQUENCE = "sequence"
    FOLLOW_INSTRUCTION = "follow_instruction"


@dataclass
class Task:
    id: int
    type: TaskType
    difficulty: int  # 1..N
    prompt: str


@dataclass
class TaskResult:
    correct: bool
    user_answer: str
    expected: str
    notes: str = ""


class TaskGenerator(Protocol):
    def generate(self, task_id: int, difficulty: int) -> Task:
        ...

    def evaluate(self, task: Task, user_answer: str) -> TaskResult:
        ...


class SequenceTaskGen:
    """
    Educational: short working-memory / sequencing task.
    Difficulty controls the length.
    """

    def __init__(self, rng: RNG) -> None:
        self.rng = rng

    def generate(self, task_id: int, difficulty: int) -> Task:
        length = max(2, 2 + difficulty)
        digits = [str(self.rng.randint(0, 9)) for _ in range(length)]
        seq = " ".join(digits)
        prompt = (
            "Memory task: Remember this sequence, then type it back.\n"
            f"Sequence: {seq}\n"
            "Now type the same digits separated by spaces:"
        )
        t = Task(id=task_id, type=TaskType.SEQUENCE, difficulty=difficulty, prompt=prompt)
        # Store expected in a simple private attribute to keep Task minimal.
        t_expected = " ".join(digits)
        setattr(t, "_expected", t_expected)
        return t

    def evaluate(self, task: Task, user_answer: str) -> TaskResult:
        expected = getattr(task, "_expected", "").strip()
        ans = " ".join(user_answer.strip().split())
        correct = ans == expected
        return TaskResult(correct=correct, user_answer=ans, expected=expected)


class FollowInstructionTaskGen:
    """
    Educational: follow a simple instruction string.
    Difficulty controls the number of steps in the instruction.
    """

    ACTIONS = ["clap", "tap", "wave", "smile", "blink"]

    def __init__(self, rng: RNG) -> None:
        self.rng = rng

    def generate(self, task_id: int, difficulty: int) -> Task:
        steps = max(1, 1 + difficulty // 2)
        actions = [self.rng.choice(self.ACTIONS) for _ in range(steps)]
        expected = " ".join(actions)
        prompt = (
            "Follow-instruction task: Type the actions in order.\n"
            f"Instruction: {expected}\n"
            "Your answer:"
        )
        t = Task(id=task_id, type=TaskType.FOLLOW_INSTRUCTION, difficulty=difficulty, prompt=prompt)
        setattr(t, "_expected", expected)
        return t

    def evaluate(self, task: Task, user_answer: str) -> TaskResult:
        expected = getattr(task, "_expected", "").strip()
        ans = " ".join(user_answer.strip().split()).lower()
        correct = ans == expected.lower()
        return TaskResult(correct=correct, user_answer=ans, expected=expected)


class TaskManager:
    """
    Chooses tasks and manages difficulty adjustments.
    """

    def __init__(self, rng: RNG, min_difficulty: int = 1, max_difficulty: int = 6) -> None:
        self.rng = rng
        self.min_difficulty = int(min_difficulty)
        self.max_difficulty = int(max_difficulty)
        self.difficulty = int(min_difficulty)
        self._task_id = 1

        self._gens: List[TaskGenerator] = [
            SequenceTaskGen(rng),
            FollowInstructionTaskGen(rng),
        ]

    def next_task(self) -> Task:
        gen = self.rng.choice(self._gens)
        t = gen.generate(self._task_id, self.difficulty)
        self._task_id += 1
        return t

    def evaluate(self, task: Task, user_answer: str) -> TaskResult:
        # Dispatch to generator based on type.
        for gen in self._gens:
            if isinstance(gen, SequenceTaskGen) and task.type == TaskType.SEQUENCE:
                return gen.evaluate(task, user_answer)
            if isinstance(gen, FollowInstructionTaskGen) and task.type == TaskType.FOLLOW_INSTRUCTION:
                return gen.evaluate(task, user_answer)
        # Fallback (shouldn't happen)
        return TaskResult(correct=False, user_answer=user_answer, expected="", notes="No evaluator found")

    def adjust_difficulty(self, success: bool) -> None:
        if success:
            self.difficulty = min(self.max_difficulty, self.difficulty + 1)
        else:
            self.difficulty = max(self.min_difficulty, self.difficulty - 1)

