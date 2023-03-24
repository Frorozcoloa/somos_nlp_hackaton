import requests
from bs4 import BeautifulSoup
from newspaper import network
from time import sleep
import random
from google_news import scrape_urls
import pandas as pd

URL_FSG = "https://informesdiscriminacion.gitanos.org/buscar-casos?combine=&field_tipos_tid=All&field_ambito_tid=All&field_ano_caso_value%5Bvalue%5D%5Byear%5D=&field_provincia_tid=All&page={}"
DOMINIAN = "https://informesdiscriminacion.gitanos.org"
def gets_links(html):
    """ This is a function that takes in a string of HTML and returns a list of links."""
    # supongamos que tenemos el html en una variable llamada 'html'
    soup = BeautifulSoup(html, 'html.parser')

    # encontrar todas las etiquetas <ul>
    lies = soup.find(id="block-system-main").find_all("li", class_="views-row")

    # iterar a través de cada etiqueta <ul> y encontrar las etiquetas <span> dentro de ella
    links = [ li.find("a")['href'] for li in lies]
    links_dominian = list(map(lambda x: DOMINIAN + x, links))
    return links_dominian
        
def save_links(links, filename):
    with open(filename, 'a') as file:
        # convertir la lista en una cadena con join()
        datos_str = '\n'.join(links) + '\n'
        # escribir la cadena en el archivo
        file.write(datos_str)

def test_links():
    for i in range(0, 183):
        url = URL_FSG.format(i)
        html = html = network.get_html_2XX_only(url)
        links_dominian = gets_links(html)
        save_links(links_dominian, "links.txt")
        with open("batch.txt", "w") as f:
            f.write(f"python scraper_FSG.py {i}")
        print(f"Batch scrapper {i}")
    
    sleep(random.randint(20, 60))

def reads_links(filename):
    """ This is a function that takes in a string of HTML and returns a list of list the links."""
    with open(filename, 'r') as file:
        # leer el archivo y convertirlo en una lista
        links = file.read().splitlines()
    sub_lists = []
    for i in range(0, len(links), 100):
        sub_lists.append(links[i:i+100])
    return sub_lists

def saves_data(sub_lists):
    for i, sub_list in enumerate(sub_lists):
        df = scrape_urls(sub_list)
        df.to_csv(f"informesdiscriminacion_{i}.csv", index=False)
        sleep(random.randint(20, 60))
        print(f"Batch {i} saved")

    

if __name__ == '__main__':
    sub_lists = reads_links("links.txt")
    saves_data(sub_lists)