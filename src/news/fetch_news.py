import requests
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import NEWSAPI_KEY, BASE_URL

class NewsAPI:
    def __init__(self):
        self.api_key = NEWSAPI_KEY
        self.base_url = BASE_URL

        if not self.api_key:
            raise ValueError("NEWSAPI_KEY not found in environment variables.")

    
    def fetch_news(self, 
                   language: str = "en", 
                   page_size: int = 50):
        
        '''
        Fetch latest news
        Optional params: {
            from_date: str (YYYY-MM-DD)
            to_date: str (YYYY-MM-DD)
            q: str (keywords)
        }

        '''
        
        endpoint = f"{self.base_url}top-headlines"
        params = {
            "country": "us",
            "category": "business",
            "language": language,
            "pageSize": page_size,
            "apiKey": self.api_key
        }

        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        return data.get("articles", [])

if __name__ == "__main__":
    # Sample use case
    news_api = NewsAPI()
    articles = news_api.fetch_news()
    with open('data/sample_news.json', 'w') as j:
        json.dump(articles, j, indent=4)
        
    for article in articles:
        print(f"Title: {article['title']}\nDescription: {article['description']}\n")

