import json
import os
from RecipeDb import RecipeDb


if __name__ == "__main__":
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    db_name = os.environ.get("DB_NAME", "crawling")
    db_host = os.environ.get("DB_HOST", "localhost")

    recipe_db = RecipeDb(db_user, db_pass, db_name, db_host)

    recipes = recipe_db.get_top_n_recipe(40)
    with open("export_top_40.json",  "w", encoding='utf8') as f:
        json.dump(recipes, f, ensure_ascii=False)
