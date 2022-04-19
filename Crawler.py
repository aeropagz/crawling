import requests
from bs4 import BeautifulSoup
from typing import Callable, List
import logging
from time import sleep
from RecipeDb import RecipeDb

logger = logging.getLogger("crawler")


class Crawler:
    def __init__(self, recipe_db: RecipeDb):
        self._db = recipe_db

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

                next_url_anchor = soup.select_one("div.ds-pagination__btn--next > a")

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

    def crawl_items(
        self, callback_list: List[Callable[[str, dict], None]], limit: int = 100
    ) -> None:
        sites = self._db.get_unvisited_sites(limit)
        url_ids = []
        crawled_data = []
        for site in sites:
            logger.info(f"🕷 Crawling website: '{site[1]}'")
            try:
                page_source = requests.get(site[1]).content
                url_ids.append(site[0])
            except Exception as e:
                print(e)
                continue
            page_model = {}

            for func in callback_list:
                func(page_source, page_model)

            page_model["url"] = site[1]
            page_model["url_id"] = site[0]
            # print(page_model)
            page_model["html"] = page_source
            crawled_data.append(page_model)
            if len(crawled_data) >= 50:
                self._db.push_crawled_urls(crawled_data)
                self._db.check_visited_sites(url_ids)
                crawled_data = []
            sleep(4)
        self._db.push_crawled_urls(crawled_data)
        self._db.check_visited_sites(url_ids)

    def validate_recipe_link(self, link: str) -> bool:
        return link.startswith("https://www.chefkoch.de/rezepte/")
