from Crawler import Crawler
from RecipeDb import RecipeDb
import argparse
import json

import os
import logging


logging.basicConfig(
    format='%(asctime)s - %(levelname)s | %(name)s: %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()]
)


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s -m [MODE]",
        description="Crawl chefkoch recipes urls or full recipes"
    )
    parser.add_argument(
        "-m", "--mode", nargs=1, type=str, choices=["url", "recipe", "export"], required=True
    )
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()

    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    db_name = os.environ.get("DB_NAME", "crawling")
    db_host = os.environ.get("DB_HOST", "localhost")

    recipe_db = RecipeDb(db_user, db_pass, db_name, db_host)
    crawler = Crawler(recipe_db)

    if "url" in args.mode:
        crawler.collect_item_links(
            "https://www.chefkoch.de/rs/s0/Rezepte.html", "ds-teaser-link", "ds-btn--control")

    elif "recipe" in args.mode:
        while True:
            crawler.crawl_items(200)
    elif "export" in args.mode:
        recipes = recipe_db.get_top_n_recipe(40)
        with open("export_top_40.json",  "w", encoding='utf8') as f:
            json.dump(recipes, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
