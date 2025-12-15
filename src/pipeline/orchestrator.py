
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

    def run_cycle(self):
        articles = self.news_api.fetch_news()

        news_articles = [
            a for a in articles if a.get("url") not in self.processed_urls
        ]

        for article in news_articles:
            self.processed_urls.add(article.get("url"))
            self._process_article(article)


        # clear processed URLs to avoid memory bloat
        if len(self.processed_urls) > 500:
            self.processed_urls = set(list(self.processed_urls)[-500:])

        print("Cycle complete. Processed articles:", len(news_articles))
        

    def _process_article(self, article: dict):
        title = article.get("title", "")
        description = article.get("description", "")
        content = f"{title}. {description}"

        sentiment_result = self.sentiment_analyzer.analyze(content)

        if sentiment_result["signal"] == "NEUTRAL":
            return  # Skip neutral articles
        
        print(f"Title: {title}")
        print(f"Sentiment: {sentiment_result['label'].upper()} (Score: {sentiment_result['score']:.4f})")
        print(f"Signal: {sentiment_result['signal']}")
        print("-" * 50)



if __name__ == "__main__":
    orchestrator = NewsOrchestrator()
    orchestrator.run_cycle()