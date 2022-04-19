from dataclasses import dataclass


@dataclass
class Ingredient:
    name: str
    amount: float
    categories: set[str]