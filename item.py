from dataclasses import dataclass
from typing import Union
from forklift import Forklift
from service_part import ServicePart
from typing import Union

@dataclass
class Item:
    product: Union['Forklift', 'ServicePart']
    quantity: int
    is_paid: bool = False
