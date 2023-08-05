from dataclasses import dataclass


@dataclass
class PlatformProductFormat:
    id: str
    name: str
    platform_id: str
    description: str
    title: str
    price: str
    pm_restaurant_id: str
    options: list
    status: bool


@dataclass
class PlatformProductOptionFormat:
    id: str
    type: str
    name: str
    description: str
    price: str
    title: str
