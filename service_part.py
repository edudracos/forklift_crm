from dataclasses import dataclass
from typing import Any

@dataclass
class ServicePart:
    id: int
    name: str
    price: float
    is_paid: bool = False
    key: Any = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "is_paid": self.is_paid,
        }
