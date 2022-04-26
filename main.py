from Crawler import Crawler
from bs4 import BeautifulSoup
import os
import logging

from extractors import *
from util import CustomFormatter

from RecipeDb import RecipeDb

logging.basicConfig(format='%(asctime)s - %(levelname)s | %(name)s: %(message)s', level=logging.INFO)









if __name__ == "__main__":
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    db_name = os.environ.get("DB_NAME", "crawling")
    db_host = os.environ.get("DB_HOST", "localhost")

    recipe_db = RecipeDb(db_user, db_pass, db_name, db_host)

    crawler = Crawler(recipe_db)
    # crawler.collect_item_links("https://www.chefkoch.de/rs/s0/Rezepte.html", "ds-teaser-link", "ds-btn--control")
    while True:
        crawler.crawl_items([get_recipe_name, get_rating, get_ingredients, get_author, get_instruction, get_tags], 200)
