from dataclasses import dataclass
from datetime import datetime
from typing import List
from item import Item

@dataclass
class Sale:
    id: int
    date: datetime
    items: List[Item]
    total_cost: float