from psycopg2 import errors, connect
from model.RecipePage import RecipePage


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

    def push_crawled_urls(self, recipes: list[RecipePage]) -> None:
        rows_affected = 0
        for recipe in recipes:
            self.__db_cur.execute("INSERT INTO recipes ( title, html, ingredients, rating, amount_ratings, "
                                  "instructions, author, url, url_id, tags, amount_comments, img, difficulty, preptime) VALUES (%s, %s, %s,%s,"
                                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                  (recipe.title, recipe.html, recipe.ingredients, recipe.rating,
                                   recipe.amount_ratings, recipe.instruction, recipe.author, recipe.url,
                                   recipe.url_id, recipe.tags, recipe.amount_comments, recipe.img, recipe.difficulty, recipe.preptime))
            rows_affected += self.__db_cur.rowcount
        if rows_affected != len(recipes):
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

    def get_top_40_recipe(self):
        self.__db_cur.execute(
            "SELECT title, author, rating, amount_ratings, ingredients, instructions, tags, img, preptime, difficulty FROM recipes "
            "WHERE rating >= 4.8 and amount_ratings >= 200 "
            "ORDER BY rating "
            "LIMIT 40"
        )
        res = self.__db_cur.fetchall()

        recipes = []
        for recipe in res:
            title, author, rating, amount_ratings, ingredients, instructions, tags, img, preptime, difficulty = recipe
            recipe_dict = {"title": title,
                           "author": author,
                           "rating": rating,
                           "amount_ratings": amount_ratings,
                           "ingredients": ingredients,
                           "instructions": instructions,
                           "tags": tags,
                           "img": img,
                           "preptime": preptime,
                           "difficulty": difficulty
                           }
            recipes.append(recipe_dict)

        return recipes
