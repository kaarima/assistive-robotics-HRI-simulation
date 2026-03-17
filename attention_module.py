from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from utils import AttentionState, RNG


@dataclass
class AttentionReading:
    state: AttentionState
    confidence: float  # 0..1
    source: str  # "sim" or "opencv"


class AttentionModule:
    """
    Engagement / attention estimator.

    Default: simple rule-based simulation (stable, deterministic with a seed).
    Optional: OpenCV face presence can be used as a crude proxy:
      face detected -> attentive-ish, else absent/distracted.
    """

    def __init__(
        self,
        rng: RNG,
        use_opencv: bool = False,
        base_attentive_prob: float = 0.78,
        distraction_spike_prob: float = 0.12,
    ) -> None:
        self.rng = rng
        self.use_opencv = bool(use_opencv)
        self.base_attentive_prob = float(base_attentive_prob)
        self.distraction_spike_prob = float(distraction_spike_prob)

        self._cv2 = None
        self._face_cascade = None
        self._cap = None

        if self.use_opencv:
            self._try_init_opencv()

    def _try_init_opencv(self) -> None:
        try:
            import cv2  # type: ignore

            self._cv2 = cv2
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                self._cap.release()
                self._cap = None
                self.use_opencv = False
        except Exception:
            self.use_opencv = False
            self._cv2 = None
            self._face_cascade = None
            self._cap = None

    def close(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
        self._cap = None

    def sense(self) -> AttentionReading:
        if self.use_opencv and self._cv2 is not None and self._face_cascade is not None and self._cap is not None:
            ok, frame = self._cap.read()
            if not ok or frame is None:
                return self._simulate()
            gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
            if len(faces) > 0:
                return AttentionReading(state=AttentionState.ATTENTIVE, confidence=0.75, source="opencv")
            # No face: could be distracted or absent; keep it simple.
            return AttentionReading(state=AttentionState.ABSENT, confidence=0.65, source="opencv")

        return self._simulate()

    def _simulate(self) -> AttentionReading:
        """
        Lightly stateful simulation: most of the time attentive, sometimes distracted.
        """
        r = self.rng.random()
        if r < self.base_attentive_prob:
            # Occasionally a short distraction spike even if generally attentive.
            if self.rng.random() < self.distraction_spike_prob:
                return AttentionReading(state=AttentionState.DISTRACTED, confidence=0.60, source="sim")
            return AttentionReading(state=AttentionState.ATTENTIVE, confidence=0.75, source="sim")

        # Not attentive: split between distracted and absent.
        if self.rng.random() < 0.55:
            return AttentionReading(state=AttentionState.DISTRACTED, confidence=0.55, source="sim")
        return AttentionReading(state=AttentionState.ABSENT, confidence=0.55, source="sim")

