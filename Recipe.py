from dataclasses import dataclass
from Ingredient import Ingredient


@dataclass(frozen=True)
class Recipe:
    id: str
    title: str
    description: str
    instruction: str
    portion: int
    ingredients: list[Ingredient]
    