from psycopg2 import errors, connect


import json


class RecipeDb:
    def __init__(self, username: str, password: str, database: str, host: str):
        self.__db_conn = None
        self.__db_cur = None
        self.__options = None
        self.__setup_db(username, password, database, host)

    def __setup_db(self, username: str, password: str, database: str, host: str) -> None:
        self.__db_conn = connect(
            f"user={username} password={password} dbname={database} host={host}")
        self.__db_cur = self.__db_conn.cursor()

    def push_new_urls(self, links: tuple[str]) -> None:

        batch_insert = ",".join([self.__db_cur.mogrify(
            "(%s, %s)", (url, False)).decode("utf-8") for url in links])
        try:
            # batch insert all urls
            self.__db_cur.execute(
                "INSERT INTO url_visited (url, visited) VALUES " + batch_insert)
            self.__db_conn.commit()

        except errors.UniqueViolation as e:
            # some urls are already saved -> find not saved urls and go again
            self.__db_conn.rollback()
            saved_urls = set([row[1] for row in self.get_all_urls()])
            unique_links = list(set(links) - saved_urls)
            if unique_links:
                self.push_new_urls(tuple(unique_links))

    def push_crawled_urls(self, page_models: list) -> None:
        rows_affected = 0
        for model in page_models:
            self.__db_cur.execute("INSERT INTO recipes ( title, html, ingredients, rating, reviews, "
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
        self.__db_cur.execute("SELECT * FROM url_visited")
        return self.__db_cur.fetchall()

    def get_unvisited_sites(self, limit=50) -> list:
        self.__db_cur.execute(
            "SELECT * FROM url_visited WHERE visited = FALSE LIMIT %s", [limit])
        return self.__db_cur.fetchall()

    def check_visited_sites(self, url_ids: list) -> None:
        for url_id in url_ids:
            self.__db_cur.execute(
                "UPDATE url_visited SET visited = TRUE WHERE id = %s", [url_id])
        self.__db_conn.commit()
