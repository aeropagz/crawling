import requests
import re
from bs4 import BeautifulSoup
from dataclasses import asdict
import logging
import base64
import requests
import json


from time import sleep
from model.RecipePage import RecipePage

from util import stripify, parse_amount
from model.Ingredient import Ingredient
from RecipeDb import RecipeDb

logger = logging.getLogger("crawler")


class Crawler:
    def __init__(self, recipe_db: RecipeDb, min_rating: float = 4.0):
        self._db = recipe_db
        self._min_rating = min_rating
        self._soup = None

    def get_last_url(self) -> str | None:
        with open("last_url.txt", "r+") as file:
            url = file.readline()
            if self.validate_recipe_link(url):
                return url

    def save_last_url(self, url: str) -> None:
        with open("last_url.txt", "w") as file:
            file.write(url)

    def collect_item_links(
        self, start_url: str, anchor_class_item: str, anchor_class_next: str
    ) -> None:
        saved_url = self.get_last_url()
        next_url = saved_url if saved_url is not None else start_url
        links = []

        try:
            while next_url:
                page_source = requests.get(next_url).content
                soup = BeautifulSoup(page_source, "html.parser")

                anchors = soup.find_all(
                    "a", class_=anchor_class_item, href=True)
                links += [
                    a["href"] for a in anchors if self.validate_recipe_link(a["href"])
                ]

                logger.info(f"{len(links)} recipe urls found")

                next_url_anchor = soup.select_one(
                    "div.ds-pagination__btn--next > a")

                if next_url_anchor is None:
                    logger.error("No link found for next recipe overview page")
                    break

                next_url = "https://www.chefkoch.de" + next_url_anchor["href"]

                if len(links) > 120:
                    self._db.push_new_urls(tuple(links))
                    links = []

        except Exception as e:
            print(e)
            with open("last_url.txt", "w") as file:
                file.write(next_url)
            self._db.push_new_urls(links)
            raise

    def crawl_items(self, limit: int = 100) -> None:
        sites = self._db.get_unvisited_sites(limit)
        url_ids = []
        crawled_data = []
        for site in sites:
            logger.info("Crawling website: '%s'", site[1])

            page_source = self.get_recipe_html(site[1]).decode("utf-8")

            url_ids.append(site[0])

            self._soup = BeautifulSoup(page_source, "html.parser")

            url = site[1]
            url_id = site[0]
            title = self.get_recipe_name()
            rating = self.get_recipe_rating()

            if rating < self._min_rating:
                # only get recipe better than min_rating
                continue

            amount_rating = self.get_recipe_amount_ratings()
            amount_comments = self.get_recipe_amount_comments()
            recipe_size = self.get_recipe_size()
            ingredients = self.get_recipe_ingredients()
            author = self.get_recipe_author()
            instruction = self.get_instruction()
            categories = self.get_tags()
            img = self.get_img()
            difficulty = self.get_difficulty()
            preptime = self.get_preptime()

            crawled_data.append(RecipePage(
                url_id,
                title,
                author,
                rating,
                amount_rating,
                amount_comments,
                ingredients,
                recipe_size,
                instruction,
                categories,
                img,
                difficulty,
                preptime,
                url,
                page_source))

            if len(crawled_data) >= 100:
                self._db.push_crawled_urls(crawled_data)
                self._db.check_visited_sites(url_ids)
                crawled_data = []
                break
            sleep(1)

        self._db.push_crawled_urls(crawled_data)
        self._db.check_visited_sites(url_ids)

    def validate_recipe_link(self, link: str) -> bool:
        return link.startswith("https://www.chefkoch.de/rezepte/")

    def get_recipe_html(self, url: str) -> str:
        try:
            page_source = requests.get(url)
        except Exception as e:
            print(e)
        return page_source.content

    def get_recipe_name(self) -> str:
        title = self._soup.find(
            "article", class_="recipe-header").findNext('h1').text
        return title

    def get_recipe_rating(self) -> float:
        rating = self._soup.find(
            "div", class_="ds-rating-avg").findNext('strong').text
        return float(rating)

    def get_recipe_amount_ratings(self) -> int:
        amount_ratings = self._soup.select(
            ".ds-rating-count span>span")[1].text.replace(".", "")
        return int(amount_ratings)

    def get_recipe_amount_comments(self) -> int:
        amount_comments = self._soup.find(
            "button", class_="bi-goto-comments").findNext("strong").text.replace(".", "")
        return int(amount_comments)

    def get_recipe_ingredients(self) -> list[Ingredient]:

        all_ing = []

        ingredients = self._soup.select(".ingredients")

        for ingredient in ingredients:
            list_of_ing = []
            # collect all rows of Ingredients table
            table_rows = ingredient.select("tbody tr")
            for row in table_rows:
                table_data = row.select("td")
                # amount can be none
                amount = table_data[0].select_one("span")

                if amount:
                    amount = stripify(amount.text)
                else:
                    amount = "1 Stk"

                ing_name = stripify(table_data[1].select_one("span").text)
                quantiy, unit = parse_amount(amount, ing_name)

                list_of_ing.append(asdict(Ingredient(ing_name, quantiy, unit)))

            all_ing += list_of_ing

        return json.dumps(all_ing)

    def get_recipe_size(self) -> int:
        recipe_size = self._soup.find("input", {"name": "portionen"})['value']
        return recipe_size

    def get_recipe_author(self) -> str:
        author = self._soup.find(
            "div", class_="recipe-author").findNext("div", class_="ds-mb-right").findNext("span")
        return author.text if author else "deleted user"

    def get_instruction(self) -> str:
        instructions = self._soup.find(
            "small", class_="ds-recipe-meta rds-recipe-meta").findNext("div").text
        instructions = re.sub(' +', ' ', instructions.strip())
        return instructions

    def get_tags(self) -> list[str]:
        tags = []
        tags_a = self._soup.find_all("a", class_="ds-tag bi-tags", href=True)
        for tag in tags_a:
            tags.append(re.sub(' +', ' ', tag.text.strip()))
        return tags

    def get_img(self) -> dict[str, str]:
        img_tag = self._soup.find("img" )
        
        data = base64.b64encode(requests.get(
            img_tag["src"]).content).decode("utf-8")
        return data

    def get_preptime(self) -> str:
        preptime = self._soup.find("span", class_="recipe-preptime")
        return preptime.text.split("\n")[1].strip()

    def get_difficulty(self) -> str:
        difficulty = self._soup.find("span", class_="recipe-difficulty")
        return difficulty.text.split("\n")[1].strip()
