import psycopg2
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Callable, List
from time import sleep


class Crawler:
    def __init__(self, username: str, password: str, database: str):
        self.__db_conn = None
        self.__db_cur = None
        self.__options = None
        self.__set_selenium_options()
        self.__setup_db(username, password, database)

    def __set_selenium_options(self):
        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument("--ignore-certificates-errors")
        self.__options.add_argument("--incognito")
        self.__options.add_argument("--headless")

    def __setup_db(self, username: str, password: str, database: str) -> None:
        self.__db_conn = psycopg2.connect(f"user={username} password={password} dbname={database}")
        self.__db_cur = self.__db_conn.cursor()

    def collect_item_links(self, start_url: str, anchor_class_item: str, anchor_class_next: str) -> None:
        driver = webdriver.Chrome("C:/chromedriver/chromedriver.exe", options=self.__options)
        links = []
        links_collected = 0
        next_url = start_url
        with open("last_url.txt", "r+") as file:
            data = file.read()
            if len(data) > 10:
                next_url = data
        try:
            while next_url:
                driver.get(next_url)
                page_source = driver.page_source
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

    def get_all_urls(self) -> list:
        self.__db_cur.execute("SELECT * FROM public.url_visited")
        return self.__db_cur.fetchall()

    def get_unvisited_sites(self) -> list:
        self.__db_cur.execute("SELECT * FROM public.url_visited WHERE visited = FALSE LIMIT 50")
        return self.__db_cur.fetchall()

    def crawl_items(self, callback_list: List[Callable[[str, dict], None]]) -> None:
        driver = webdriver.Chrome("C:/chromedriver/chromedriver.exe", options=self.__options)
        sites = self.get_unvisited_sites()
        for site in sites:
            driver.get(site[1])
            page_source = driver.page_source
            page_model = {}
            for func in callback_list:
                func(page_source, page_model)
        sleep(1)






