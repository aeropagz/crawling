from Crawler import Crawler
from bs4 import BeautifulSoup
import re


def get_recipe_name(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "lxml")
    title = soup.find("article", class_="recipe-header").findNext('h1').text
    model["title"] = title


def get_rating(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "lxml")
    rating = soup.find("div", class_="ds-rating-avg").findNext('strong').text
    amount_rating = list(soup.find("div", class_="ds-rating-count").descendants)[6]
    amount_comments = soup.find("button", class_="bi-goto-comments").findNext("strong").text
    try:
        model["rating"] = float(rating)
        model["amount_rating"] = int(amount_rating)
        model["amount_comments"] = int(amount_comments)
    except Exception as e:
        print(e)
        raise


def get_ingredients(page_source: str, model: dict) -> None:
    all_ing = {}
    soup = BeautifulSoup(page_source, "lxml")
    ingr_for_x = soup.find("input", {"name": "portionen"})['value']
    ingredients = soup.select(".ingredients")
    for ingredient in ingredients:
        list_of_ing = []
        recipe_part = ingredient.select_one("thead tr th h3")
        # if Heading for Ingredients available get it
        if recipe_part:
            recipe_part_name = recipe_part.text
        else:
            recipe_part_name = "main"
        # collect all rows of Ingredients table
        table_rows = ingredient.select("tbody tr")
        for row in table_rows:
            table_data = row.select("td")
            amount = re.sub(' +', ' ', table_data[0].select_one("span").text).strip()
            ing = re.sub(' +', ' ', table_data[1].select_one("span").text).strip()
            list_of_ing.append({ing: amount})
        all_ing[recipe_part_name] = list_of_ing
        all_ing['persons'] = ingr_for_x
    model['ingredients'] = all_ing


def get_author(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "lxml")
    author = soup.select_one(".user-box ds-mb-right ds-copy-link bi-profile")
    if author:
        model['author'] = author
    else:
        model['author'] = "deleted user"
    print(author)


if __name__ == "__main__":
    crawler = Crawler("admin", "brassica", "crawling")
    # crawler.collect_item_links("https://www.chefkoch.de/rs/s0/Rezepte.html", "rsel-recipe", "bi-paging-next")
    crawler.crawl_items([get_recipe_name, get_rating, get_ingredients, get_author])
