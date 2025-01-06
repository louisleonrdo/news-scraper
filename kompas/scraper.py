from newspaper import Article
from bs4 import BeautifulSoup
import re
# import nltk
# nltk.download('punkt_tab')

url = "https://nasional.kompas.com/read/2025/01/02/11322451/57-persen-hasil-pilkada-2024-digugat-ke-mk-terbanyak-pemilihan-bupati"

article = Article(url, language='id')
article.download()  
article.parse()  

cleaned_text = re.sub(r'^\s*Baca juga.*\n?', '', article.text, flags=re.MULTILINE)

# soup = BeautifulSoup(article.html, 'html.parser')

# for recommendation in soup.find_all('div', class_='inner-link-baca-juga'):  
#     recommendation.decompose()



print("Title:", article.title)
print("Authors:", article.authors)
print("Publish date:", article.publish_date)

cleaned_text = cleaned_text.replace('\n', ' ')
print(cleaned_text)