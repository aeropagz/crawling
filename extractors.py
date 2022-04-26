from bs4 import BeautifulSoup
import re

def get_recipe_name(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "html.parser")
    title = soup.find("article", class_="recipe-header").findNext('h1').text
    model["title"] = title


def get_rating(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "html.parser")
    rating = soup.find("div", class_="ds-rating-avg").findNext('strong').text
    reviews = soup.select(".ds-rating-count span>span")[1].text.replace(".", "")
    amount_comments = soup.find("button", class_="bi-goto-comments").findNext("strong").text.replace(".", "")
    try:
        model["rating"] = float(rating)
        model["reviews"] = int(reviews)
        model["amount_comments"] = int(amount_comments)
    except Exception as e:
        print(e)
        raise


def get_ingredients(page_source: str, model: dict) -> None:
    all_ing = {}
    soup = BeautifulSoup(page_source, "html.parser")
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
            # amount can be none
            amount = table_data[0].select_one("span")
            if amount:
                amount = re.sub(' +', ' ', amount.text).strip()
            else:
                amount = ""
            ing = re.sub(' +', ' ', table_data[1].select_one("span").text).strip()
            list_of_ing.append({ing: amount})
            
        all_ing[recipe_part_name] = list_of_ing
        all_ing['persons'] = ingr_for_x
    model['ingredients'] = all_ing


def get_author(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "html.parser")
    author = soup.find("div", class_="recipe-author").findNext("div", class_="ds-mb-right").findNext("span")
    if author:
        model['author'] = author.text
    else:
        model['author'] = "deleted user"


def get_instruction(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "html.parser")
    instructions = soup.find("small", class_="ds-recipe-meta rds-recipe-meta").findNext("div").text
    instructions = re.sub(' +', ' ', instructions.strip())
    model['instructions'] = instructions


def get_tags(page_source: str, model: dict) -> None:
    tags = []
    soup = BeautifulSoup(page_source, "html.parser")
    tags_a = soup.find_all("a", class_="ds-tag bi-tags", href=True)
    for tag in tags_a:
        tags.append(re.sub(' +', ' ', tag.text.strip()))
    model['tags'] = tags