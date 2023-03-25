import requests
from newspaper import Article, network, configuration
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://informesdiscriminacion.gitanos.org/informes/{}"
YEARS = range(2005,2022+1)

def get_html_2XX_only(url, config=None, response=None):
    """Consolidated logic for http requests from newspaper. We handle error cases:
    - Attempt to find encoding of the html by using HTTP header. Fallback to
      'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.
    """
    config = config or configuration.Configuration()
    useragent = config.browser_user_agent
    timeout = config.request_timeout
    proxies = config.proxies
    headers = config.headers

    if response is not None:
        return response
    requests_kwar = network.get_request_kwargs(timeout, useragent, proxies, headers)
    response = requests.get(
        url=url, **requests_kwar)

    return response

def gets_link_pdf(soup,year):
    link = soup.find("span", {"class": "file"}).find("a")
    href = link.get("href")
    response = get_html_2XX_only(href)
    with open(f"{year}.pdf", "wb") as f:
        f.write(response.content)
    
    

values = []

for year in YEARS:
    url = URL.format(year)
    article = Article(url)
    article.download()
    article.parse()
    info = {
        "title": article.title,
        "content": article.text,
    }
    soup = BeautifulSoup(article.html, "html.parser")
    gets_link_pdf(soup, year)
    values.append(info)

pd.DataFrame(values).to_csv("scrapper_info.csv", index=False)
    