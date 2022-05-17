from Crawler import Crawler
from RecipeDb import RecipeDb

import os
import logging


logging.basicConfig(
    format='%(asctime)s - %(levelname)s | %(name)s: %(message)s', level=logging.INFO)


if __name__ == "__main__":
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    db_name = os.environ.get("DB_NAME", "crawling")
    db_host = os.environ.get("DB_HOST", "localhost")

    recipe_db = RecipeDb(db_user, db_pass, db_name, db_host)

    crawler = Crawler(recipe_db)
    # crawler.collect_item_links("https://www.chefkoch.de/rs/s0/Rezepte.html", "ds-teaser-link", "ds-btn--control")
    while True:
        crawler.crawl_items(200)
