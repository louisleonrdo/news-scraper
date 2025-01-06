import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import json


# Initialization
current_date = date.today()
articles = []
filename = current_date.strftime("%Y-%m-%d")


def extract(selectedDate, count, filter='all'):
    url = f"https://indeks.kompas.com/?site={filter}&date={selectedDate}&page={count}"
    response = requests.get(url)

    return response


def transform(response):
    articles = []

    soup = BeautifulSoup(response.text, 'html.parser')
    newsBox = soup.find_all('div', class_='articleItem')

    for news in newsBox:
        link = news.find('a', class_='article-link')['href']
        title = news.find('h2', class_='articleTitle').get_text()
        articleType = news.find('div', class_='articlePost-subtitle').get_text()
        date = news.find('div', class_='articlePost-date').get_text()

        articles.append({
            'link': link,
            'title': title,
            'article_type': articleType,
            'date': date    
        })

    return articles

def write_to_json(filename, new_articles):

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    

    unique_articles = []
    existing_links = { article['link'] for article in existing_data }


    for article in new_articles:
        if article['link'] not in existing_links:
            unique_articles.append(article)
            existing_links.add(article['link'])

    if unique_articles:
        existing_data.extend(unique_articles)
        with open(filename, 'w') as file:
            json.dump(existing_data, file, indent=4)
        print(f"{len(unique_articles)} new articles added to {filename}")
    else:
        print("No new articles to add")

def continuousExtraction():
    count = 1
    total_articles = 0

    while True:
        response = extract(current_date, count)
        articles = transform(response)
        total_articles += len(articles)

        write_to_json(f"storage/{filename}.json", articles)

        count += 1

        if not articles:
            break

    print(f"got {total_articles} articles from {count} pages")



if __name__ == "__main__":
    if not os.path.exists("storage"):
        os.makedirs("storage", exist_ok=True)

    continuousExtraction()


