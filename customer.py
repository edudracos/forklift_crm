from typing import List
from forklift import Forklift
from service_part import ServicePart
from sale import Sale

class Customer:
    def __init__(self, id: int, name: str, contact_details: str, forklifts: List[Forklift] = [], service_parts: List[ServicePart] = [], sales: List[Sale] = []):
        self.id = id
        self.name = name
        self.contact_details = contact_details
        self.forklifts = forklifts
        self.service_parts = service_parts
        self.sales = sales

    def add_forklift(self, forklift: Forklift) -> None:
        self.forklifts.append(forklift)

    def add_service_part(self, service_part: ServicePart) -> None:
        self.service_parts.append(service_part)

    def add_sale(self, sale: Sale) -> None:
        self.sales.append(sale)

    @property
    def total_owed(self) -> float:
        return sum(sale.total_cost for sale in self.sales)

    def mark_service_as_paid(self, service_name: str) -> None:
        for service in self.service_parts:
            if service.name == service_name:
                service.is_paid = True
                return

    def mark_forklift_as_paid(self, forklift_name: str) -> None:
        for forklift in self.forklifts:
            if forklift.name == forklift_name:
                forklift.is_paid = True
                return

    def mark_item_as_paid(self, item_name: str) -> None:
        for sale in self.sales:
            for item in sale.items:
                if item.product.name == item_name:
                    item.is_paid = True
                    return
