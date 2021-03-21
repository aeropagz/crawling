from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

client = MongoClient()
recipes_db = client.crawling.recipes

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificates-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome("C:/chromedriver/chromedriver.exe", options=options)
driver.get("https://www.chefkoch.de/rs/s0/Rezepte.html")

recipe_links = []
next_page_link = "https://www.chefkoch.de/rs/s0/Rezepte.html"

while next_page_link:
    driver.get(next_page_link)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    for a in soup.find_all('a', class_="rsel-recipe", href=True):
        recipe_links.append(a['href'])
    next_page_link = soup.find("a", class_="bi-paging-next", href=True)['href']
    print(len(recipe_links))







