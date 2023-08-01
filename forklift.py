from dataclasses import dataclass
from typing import Any

@dataclass
class Forklift:
    id: int
    name: str
    price: float
    key: Any = None
