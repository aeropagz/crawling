from dataclasses import dataclass
from model.Ingredient import Ingredient


@dataclass(frozen=True)
class Recipe:
    id: str
    title: str
    description: str
    instruction: str
    portion: int
    ingredients: list[Ingredient]
    categories: str
