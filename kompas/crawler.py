import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import sys
import os
import json
from newspaper import Article
import re
import time



def log(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {level.upper():<8} {message}")


# # Initialization
# current_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date() if len(sys.argv) > 1 else date.today()

# print(current_date)
# articles = []
# filename = current_date.strftime("%Y-%m-%d")
# print(current_date)


def extract(selectedDate, count, filter='all'):
    url = f"https://indeks.kompas.com/?site={filter}&date={selectedDate}&page={count}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/',  
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)

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

        log('info', f'Successfully added {len(unique_articles)} new articles')

        return 1
    else:
        log('info', f'No new articles to add')

        return 0

def extract_kompas_articles_index(selected_date, output_index_path):
    log('INFO', f"Starting index extraction for date: {selected_date}")

    count = 1
    total_articles = 0

    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    isScraping = True

    all_raw_index_articles = []

    while isScraping:
        response = extract(selected_date, count)
        articles = transform(response)
        total_articles += len(articles)

        all_raw_index_articles.append(articles)
        # isScraping = write_to_json(output_index_path, articles)
        log('info', f'Successfully added {len(articles)} new articles')

        count += 1

        if not articles:
            break

    log('info', f'Successfully scraped through {count} pages with {total_articles} articles')

    with open(output_index_path, 'w', encoding='utf-8') as f:
        json.dump(all_raw_index_articles, f, indent=4, ensure_ascii=False)
    
    log('INFO', f"Finished index extraction. Total raw index articles scraped: {len(all_raw_index_articles)}. Saved to {output_index_path}")
    
    return output_index_path

def extract_article_content(input_index_path, output_content_path):

    log('INFO', f"Starting content extraction from {input_index_path}")
    
    with open(input_index_path, 'r', encoding='utf-8') as f:
        index_articles = json.load(f)
    
    full_articles_data = []

    total_articles = len(index_articles)

    for i, article_meta in enumerate(index_articles):
        url = article_meta['link']
        log('INFO', f"({i+1}/{total_articles}) Scraping content for: {url}")

    # for article in index_articles:

        article = Article(url, language='id')
        article.download()  
        article.parse()  

        cleaned_text = re.sub(r'^\s*Baca juga.*\n?', '', article.text, flags=re.MULTILINE)

        article_meta['authors'] = article.authors
        article_meta['publish_date'] = article.publish_date
        article_meta['content'] = cleaned_text

        full_articles_data.append(article_meta)

        time.sleep(0.5) 
        
    with open(output_content_path, 'w', encoding='utf-8') as f:
        json.dump(full_articles_data, f, indent=4, ensure_ascii=False)
    
    log('INFO', f"Finished content extraction. Total articles with content: {len(full_articles_data)}. Saved to {output_content_path}")


if __name__ == "__main__":
    if not os.path.exists("storage"):
        os.makedirs("storage", exist_ok=True)

    extract_kompas_articles_index()


