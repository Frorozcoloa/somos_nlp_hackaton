""" 
Este es el scrapper usado para descargar las noticias de google news
"""
import uuid
import traceback
import os
import pandas as pd
from GoogleNews import GoogleNews
import newspaper as ns
import click 
from datetime import datetime

def scrape_urls(webpage_urls):
    """
    Utiliza los webpages para luego scraper y asignar una categoria a la noticia
    Args:
        webpage_urls (list): Urls a las cuales se le quieren hacer los scraping
        category (str): nombre de la categoria
    Returns:
        df: DataFrame con las noticas no duplicadadas
    """    
    scraped_info = {}

    for i,url in enumerate(webpage_urls):
        try:
            print(i)
            print('-'*50)
            print(url)
            article = ns.Article(url)
            article.download()
            article.parse()
            
            news_date = datetime.strftime(article.publish_date, "%Y-%m-%d")

            print(news_date)
            scraped_info[i] = {'news_id': uuid.uuid4(),
                            'news_url_absolute': url,
                            'news_init_date' : news_date,
                            'news_final_date' : news_date,
                            'news_title':article.title,
                            'news_text_content' : article.text,
                                }
        except:
            print(traceback.print_exc())
    df = pd.DataFrame.from_records(scraped_info).T
    scraped_deduped = df.drop_duplicates(subset=['news_url_absolute'])
    print(f'Amount of news scraped: {len(scraped_deduped)}')
    return scraped_deduped

#Settings
googlenews = GoogleNews(lang='es', region="ES", encode="utf-8")

def gets_links(query):
    """
    Aquí nos conectamos a la api y extraemos los links de las noticias, recomendación, en el Query
    poner el tecto que se quiere sacar de google
    """
    googlenews.search(query)
    googlenews.set_time_range("01/09/2022", "02/09/2022")
    links = []
    for page in range(1,35):
        googlenews.get_page(page)
        links += googlenews.get_links()[1:]
        print(f"\t\t{page}")
    googlenews.clear()
    print("Noticias sacasdas de google")
    return list(set(links))

@click.command()
@click.option("--query", type=str)
@click.option("--csv_path",type=str)
#googlenews.py --category innovacion --query transformacion+digital+empresarial --csv_path elpais_transdigiemp.csv
def main(query,csv_path):
    """
    Esta función recibe los valores por consola y empieza el scraping
    Ejemplo : googlenews.py --category innovacion --query transformacion+digital+empresarial --csv_path gooogle_news.csv
    """
    print(query)
    webpage_urls = gets_links(query)
    scraped_deduped = scrape_urls(webpage_urls)
    print(f'SCRAPED SEARCH QUERY {query}')
    scraped_deduped.to_csv(csv_path,index=False)

if __name__ == '__main__':
    main()