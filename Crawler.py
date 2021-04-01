import psycopg2
import requests
from bs4 import BeautifulSoup
from typing import Callable, List
from time import sleep
import json


class Crawler:
    def __init__(self, username: str, password: str, database: str):
        self.__db_conn = None
        self.__db_cur = None
        self.__options = None
        self.__setup_db(username, password, database)

    def __setup_db(self, username: str, password: str, database: str) -> None:
        self.__db_conn = psycopg2.connect(f"user={username} password={password} dbname={database} host=192.168.50.72")
        self.__db_cur = self.__db_conn.cursor()

    def collect_item_links(self, start_url: str, anchor_class_item: str, anchor_class_next: str) -> None:
        links = []
        links_collected = 0
        next_url = start_url
        with open("last_url.txt", "r+") as file:
            data = file.read()
            if len(data) > 10:
                next_url = data
        try:
            while next_url:
                page_source = requests.get(next_url).content
                soup = BeautifulSoup(page_source, "lxml")

                for a in soup.find_all("a", class_=anchor_class_item, href=True):
                    links.append(a["href"])
                    links_collected += 1
                next_url = soup.find("a", class_=anchor_class_next, href=True)["href"]

                if len(links) > 120:
                    self.push_new_urls(links)
                    links = []
                print(links_collected)
        except Exception as e:
            print(e)
            with open("last_url.txt", "w") as file:
                file.write(next_url)
            self.push_new_urls(links)
            print(page_source)
            raise

    def push_new_urls(self, links: list) -> None:
        unique_links = list(set(links) - set(self.get_all_urls()))
        for link in unique_links:
            self.__db_cur.execute("INSERT INTO public.url_visited (url, visited) VALUES (%s, %s)",
                                  (link, False))
        self.__db_conn.commit()

    def push_crawled_urls(self, page_models: list) -> None:
        rows_affected = 0
        for model in page_models:
            self.__db_cur.execute("INSERT INTO public.recipes ( title, html, ingredients, rating, reviews, "
                                  "instructions, author, url, url_id, tags, amount_comments) VALUES (%s, %s, %s,%s,"
                                  "%s,%s,%s,%s,%s,%s,%s)",
                                  (model["title"], model["html"], json.dumps(model["ingredients"]), model["rating"],
                                   model["reviews"], model["instructions"], model["author"], model["url"],
                                   model["url_id"], model["tags"], model["amount_comments"]))
            rows_affected += self.__db_cur.rowcount
        if rows_affected != len(page_models):
            print("Something went wrong during upload crawled data")
            print("affected rows are not equal to passed-in pages")
            raise
        self.__db_conn.commit()

    def get_all_urls(self) -> list:
        self.__db_cur.execute("SELECT * FROM public.url_visited")
        return self.__db_cur.fetchall()

    def get_unvisited_sites(self, limit=50) -> list:
        self.__db_cur.execute("SELECT * FROM public.url_visited WHERE visited = FALSE LIMIT %s", [limit])
        return self.__db_cur.fetchall()

    def check_visited_sites(self, url_ids: list) -> None:
        for url_id in url_ids:
            self.__db_cur.execute("UPDATE public.url_visited SET visited = TRUE WHERE id = %s", [url_id])
        self.__db_conn.commit()

    def crawl_items(self, callback_list: List[Callable[[str, dict], None]], limit: int = 100) -> None:
        sites = self.get_unvisited_sites(limit)
        url_ids = []
        crawled_data = []
        for site in sites:
            print(site[1])
            try:
                page_source = requests.get(site[1]).content
                url_ids.append(site[0])
            except Exception as e:
                print(e)
                continue
            page_model = {}

            for func in callback_list:
                func(page_source, page_model)

            page_model['url'] = site[1]
            page_model['url_id'] = site[0]
            # print(page_model)
            page_model['html'] = page_source
            crawled_data.append(page_model)
            if len(crawled_data) >= 50:
                self.push_crawled_urls(crawled_data)
                self.check_visited_sites(url_ids)
                crawled_data = []
            sleep(4)
            self.push_crawled_urls(crawled_data)
            self.check_visited_sites(url_ids)
