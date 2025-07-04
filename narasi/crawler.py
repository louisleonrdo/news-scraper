import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import json

# Initialization
current_date = date.today()
filename = current_date.strftime("%Y-%m-%d")
# current_date = "2025-03-13"
# filename = current_date
param = {
    'limit': 10,
    'isText': "true",
    'isVideo': "false",
    'category': '',
    'pageCount': 1,
    'channel': 'news'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',    
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,fr;q=0.8,id;q=0.7,ms;q=0.6",
    "if-none-match": "W/\"1eec7-kSqzqozcK0/nELSsFKLfAS8TaA0\"",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "referer": "https://narasi.tv/"  
}


def extract(selectedDate, count, filter='news'):
    try:
        url = f"https://gateway.narasi.tv/core/api/articles?sort=publishDate&dir=DESC&limit={param['limit']}&isText={param['isText']}&isVideo={param['isVideo']}&category={param['category']}&page={count}&publishDate={selectedDate}&navbar={filter}"
        print(url)
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}") 
    except Exception as e:
        print(f"An error occurred: {e}") 




def transform(response):
    articles = []

    
    for news in response['data']:
        title = news['title']
        desc = news['short']
        articleType = news['category']['title']
        channel = news['channel']['slug']
        link = f"https://narasi.tv/read/{channel}/{news['slug']}"
        date = news['createdAt']
        author = news['author']

        articles.append({
            'title': title,
            'article_type': articleType,
            'date': date,
            'author': author,
            'link': link,
            'desc': desc
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

        if count > response['meta']['pages']:
            break

    print(f"got {total_articles} articles from {count} pages")



if __name__ == "__main__":
    if not os.path.exists("storage"):
        os.makedirs("storage", exist_ok=True)

    continuousExtraction()

    
