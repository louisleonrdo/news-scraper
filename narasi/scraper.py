from newspaper import Article
import requests

# Custom function to set a longer timeout
def set_custom_timeout(article, timeout=20):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    article.session = session
    article.timeout = timeout  # Extend the timeout duration

# Your target URL
url = "https://narasi.tv/read/narasi-daily/alasan-mengapa-mk-hapus-presidential-threshold-pemilu-tidak-adil-hingga-memperuncing-polarisasi"

article = Article(url, language='id')

# Set custom timeout
set_custom_timeout(article, timeout=20)

try:
    article.download()
    article.parse()
    print("Title:", article.title)
    print("Text:", article.text)
except Exception as e:
    print(f"An error occurred: {e}")
