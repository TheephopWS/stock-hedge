
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from news.fetch_news import NewsAPI
from news.sentiment import SentimentAnalyzer

class NewsOrchestrator:
    def __init__(self):
        self.news_api = NewsAPI()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.processed_urls = set() # Keep to set for uniqueness
        self.bullish_articles = set()
        self.bearish_articles = set()
        self.all_articles = list()

    def get_num_bullish_articles(self):
        return len(self.bullish_articles)
    
    def get_num_bearish_articles(self):
        return len(self.bearish_articles)

    def run_cycle(self):
        articles = self.news_api.fetch_news(page_size=100)

        news_articles = [
            a for a in articles if a.get("url") not in self.processed_urls
        ]

        for article in news_articles:
            self.processed_urls.add(article.get("url"))
            self._process_article(article)


        # clear processed URLs to avoid memory bloat
        if len(self.processed_urls) > 500:
            self.processed_urls = set(list(self.processed_urls)[-500:])

        output_path = Path(__file__).parent.parent / "data" / "daily_news.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(self.all_articles, f, indent=4)

        print("Cycle complete. Processed articles:", len(news_articles))
        print("Number of Bullish articles:", self.get_num_bullish_articles())
        print("Number of Bearish articles:", self.get_num_bearish_articles())

    def _process_article(self, article: dict):
        title = article.get("title", "")
        description = article.get("description", "")
        content = f"{title}. {description}"

        sentiment_result = self.sentiment_analyzer.analyze(content)

        if sentiment_result["signal"] == "NEUTRAL":
            return  # Skip neutral articles
        
        elif sentiment_result["signal"] == "BULLISH":
            self.bullish_articles.add(article.get("url"))

        elif sentiment_result["signal"] == "BEARISH":
            self.bearish_articles.add(article.get("url"))
        
        print(f"Title: {title}")
        print(f"Sentiment: {sentiment_result['label'].upper()} (Score: {sentiment_result['score']:.4f})")
        print(f"Signal: {sentiment_result['signal']}")
        print("-" * 50)

        self.all_articles.append({
            "title": title,
            "sentiment": sentiment_result['label'].upper(),
            "score": sentiment_result['score'],
            "signal": sentiment_result['signal']
        })