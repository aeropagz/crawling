from dataclasses import dataclass
from model.Ingredient import Ingredient


@dataclass(frozen=True)
class RecipePage:
    url_id: str
    title: str
    author: str
    rating: float
    amount_ratings: int
    amount_comments: int
    ingredients: str
    recipe_size: int
    instruction: str
    tags: list[str]
    img: str
    difficulty: str
    preptime: str
    url: str
    html: bytes
