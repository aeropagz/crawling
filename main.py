from Crawler import Crawler
from bs4 import BeautifulSoup


def get_recipe_name(page_source: str, model: dict) -> None:
    soup = BeautifulSoup(page_source, "lxml")
    title = soup.find("article", class_="recipe-header").findNext('h1').text
    print(title)
    model["title"] = title


if __name__ == "__main__":
    crawler = Crawler("admin", "brassica", "crawling")
    # crawler.collect_item_links("https://www.chefkoch.de/rs/s0/Rezepte.html", "rsel-recipe", "bi-paging-next")
    crawler.crawl_items([get_recipe_name])
