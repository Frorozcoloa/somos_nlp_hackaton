import pandas as pd
from newspaper import Article, network
from bs4 import BeautifulSoup
from google_news import scrape_urls
URL = "https://www.gitanos.org/actualidad/prensa/comunicados/"
HOST = "https://www.gitanos.org"

def gets_linsk(url):
    article = Article(url)
    article.download()
    soup = BeautifulSoup(article.html, 'html.parser')
    links_bs  = soup.find("div", {"id": "mainContent"}).find_all("a")
    links = [link.get("href") for link in links_bs]
    links = list(filter(lambda x: x.split("/")[1] == "actualidad", links))
    links_host = [HOST + link for link in links]
    return links_host


if __name__ == "__main__":
    links = gets_linsk(URL)
    df = scrape_urls(links)
    df.to_csv("gitanosORG.csv", index=False)