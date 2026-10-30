from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Detection:
    kind: str                 # "vehicle" | "animal" | "plate"
    label: str
    confidence: float
    bbox: tuple               # (x1, y1, x2, y2) in pixels
    linked_vehicle: Optional[int] = None   # index of vehicle for plates
    extra: dict = field(default_factory=dict)
