from dataclasses import dataclass
from model.Ingredient import Ingredient


@dataclass(frozen=True)
class RecipePage:
    url_id: str
    author: str
    rating: float
    amount_ratings: int
    amount_comments: int
    ingredients: list[Ingredient]
    recipe_size: int
    instruction: str
    tags: list[str]
    url: str
    html: bytes





