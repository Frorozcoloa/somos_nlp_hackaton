import traceback
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

def gets_body(soup):
    content = soup.find("div", class_="group-contenido-datos")
    # The hechos are fix in the html
    hechos = content.find("div", class_="field-name-body").find_all("p")
    hechos = " ".join([p.text for p in hechos])
    
    intervenion = content.find("div", class_="field-name-field-intervencion")
    resultado = content.find("div", class_="field-name-field-resultado")
    
    if  intervenion:
        intervenion = intervenion.find_all("p")
        intervenion = " ".join([p.text for p in intervenion])
  
    if resultado:
        resultado = resultado.find_all("p")
        resultado = " ".join([p.text for p in resultado])
    info_body = {
        "hechos": hechos,
        "intervencion": intervenion,
        "resultado": resultado
    }
    return info_body 

def get_datos(soup):
    datos = soup.find("div", class_="group-datos")
    colum_one = datos.find("div", class_="group-columna-uno")
    column_two = datos.find("div", class_="group-columna-dos")
    
    dates = colum_one.find_all("span", class_="date-display-single")
    # Gets the dates
    if len(dates) == 2:
        fecha_hechos = dates[0]["content"]
        fecha_denuncia = dates[0]["content"]
    elif len(dates) == 1:
        fecha_hechos = dates[0]["content"]

    provincia = colum_one.find("div", class_="field-name-field-provincia")
    if provincia:
        provincia = provincia.find("div", class_="field-item").text

    # Gets the column two
    events  = column_two.find_all("div", class_="even")
    if len(events)>=3:
        ambito = events.pop(0).text
        tipo_desciminacion = events.pop(0).text
        #Found the links of references
        reference = []
        for event in events:
            a = event.find("a")
            if a:
                reference.append(a["href"])
    elif len(events) == 2:
        ambito = events[0].text
        tipo_desciminacion = events[1].text
        reference = None
    elif len(events) == 1:
        ambito = events[0].text
        tipo_desciminacion = None
        reference = None
    info = {
        "fecha_hechos": fecha_hechos,
        "fecha_denuncia": fecha_denuncia,
        "provincia": provincia,
        "ambito": ambito,
        "tipo_desciminacion": tipo_desciminacion,
        "reference": reference
    }
    return info

def saves_data(sub_lists, going=0):
    for i, sub_list in enumerate(sub_lists):
        values = []
        for link in sub_list:
            print(link)
            try:
                html = network.get_html_2XX_only(link)
                soup = BeautifulSoup(html, 'html.parser')
                info_body = gets_body(soup)
                info_datos = get_datos(soup)
                info = {**info_body, **info_datos} # merge the two dictionaries
                info["link"] = link
                values.append(info)
            except AttributeError:
                print(traceback.print_exc())
                with open(file="error.txt", mode="a") as f:
                    f.write(f"{link}\n")
        df = pd.DataFrame(values)
        df.to_csv(f"data_discriminacion_v2_{going+i}.csv", index=False)
        print(f"Batch {going+i} saved")

    

if __name__ == '__main__':
    going= 0
    sub_lists = reads_links("links.txt")
    saves_data(sub_lists[going:], going)