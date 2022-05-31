from dataclasses import dataclass
import string


@dataclass(frozen=True)
class Ingredient:
    name: str
    amount: float
    unit: str
    categories: list
