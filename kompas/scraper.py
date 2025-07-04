from newspaper import Article
import re
import json


filename = "2025-03-28"
with open("storage/2025-07-01.json", "r", encoding="utf-8") as file:
    data = json.load(file)  # Converts JSON into a Python list



for datum in data:
    print(datum['link'])

url = data[0]['link']

article = Article(url, language='id')
article.download()  
article.parse()  

cleaned_text = re.sub(r'^\s*Baca juga.*\n?', '', article.text, flags=re.MULTILINE)

    

print("Title:", article.title)
print("Authors:", article.authors)
print("Publish date:", article.publish_date)


cleaned_text = cleaned_text.replace('\n', ' ')
print(cleaned_text)