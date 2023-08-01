from dataclasses import dataclass
from typing import Any

@dataclass
class ServicePart:
    id: int
    name: str
    price: float
    key: Any = None
