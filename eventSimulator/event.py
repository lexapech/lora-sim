from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class DiscreteEvent:
    creationTime: float = field(compare=False, default=0)
    triggerTime: float = 0
    tags: list = field(compare=False, default_factory=lambda: [])
    sender: object = field(compare=False, default=None)
    data: object = field(compare=False, default=None)
