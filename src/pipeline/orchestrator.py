
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from news.fetch_news import NewsAPI
from news.sentiment import SentimentAnalyzer
from pipeline.tickers import get_tickers_sentiment, TickerExtractor

class NewsOrchestrator:
    def __init__(self):
        self.news_api = NewsAPI()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ticker_extractor = TickerExtractor()
        self.processed_urls = set() # Keep to set for uniqueness
        self.bullish_articles = set()
        self.bearish_articles = set()
        self.all_articles = list()
        self.ticker_impacts = {}  # {ticker: {"positive": count, "negative": count}}

    def get_num_bullish_articles(self):
        return len(self.bullish_articles)
    
    def get_num_bearish_articles(self):
        return len(self.bearish_articles)

    def get_ticker_summary(self) -> dict:
        return self.ticker_impacts
    
    def get_most_affected_tickers(self, top_n: int = 10) -> list[dict]:
        ticker_list = []
        for ticker, impacts in self.ticker_impacts.items():
            total = impacts["positive"] + impacts["negative"]
            net_sentiment = impacts["positive"] - impacts["negative"]
            ticker_list.append({
                "ticker": ticker,
                "total_mentions": total,
                "positive_mentions": impacts["positive"],
                "negative_mentions": impacts["negative"],
                "net_sentiment": net_sentiment,
                "sentiment_label": "bullish" if net_sentiment > 0 else "bearish" if net_sentiment < 0 else "neutral"
            })
        
        # Sort by total mentions descending
        ticker_list.sort(key=lambda x: x["total_mentions"], reverse=True)
        return ticker_list[:top_n]

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
        
        most_affected = self.get_most_affected_tickers(top_n=5)
        if most_affected:
            print("\nTop Affected Tickers:")
            for t in most_affected:
                print(f"  {t['ticker']}: {t['total_mentions']} mentions "
                      f"(+{t['positive_mentions']}/-{t['negative_mentions']}) -> {t['sentiment_label']}")

    def _process_article(self, article: dict):
        title = article.get("title", "")
        description = article.get("description", "")
        content = f"{title}. {description}"

        sentiment_result = self.sentiment_analyzer.analyze(content)
        
        ticker_info = get_tickers_sentiment(
            title=title,
            description=description,
            sentiment_result=sentiment_result,
            extractor=self.ticker_extractor
        )

        if sentiment_result["signal"] == "NEUTRAL":
            return  # Skip neutral articles
        
        elif sentiment_result["signal"] == "BULLISH":
            self.bullish_articles.add(article.get("url"))

        elif sentiment_result["signal"] == "BEARISH":
            self.bearish_articles.add(article.get("url"))
        
        # Update ticker impact tracking
        for ticker_impact in ticker_info["tickers"]:
            ticker = ticker_impact.ticker
            if ticker not in self.ticker_impacts:
                self.ticker_impacts[ticker] = {"positive": 0, "negative": 0}
            
            if ticker_impact.impact == "positive":
                self.ticker_impacts[ticker]["positive"] += 1
            elif ticker_impact.impact == "negative":
                self.ticker_impacts[ticker]["negative"] += 1
        
        print(f"Title: {title}")
        print(f"Sentiment: {sentiment_result['label'].upper()} (Score: {sentiment_result['score']:.4f})")
        print(f"Signal: {sentiment_result['signal']}")
        
        if ticker_info["has_tickers"]:
            ticker_symbols = [t.ticker for t in ticker_info["tickers"]]
            print(f"Tickers: {', '.join(ticker_symbols)}")
            if ticker_info["primary_ticker"]:
                print(f"Primary Ticker: {ticker_info['primary_ticker']}")
            if ticker_info["affected_positively"]:
                print(f"  Positively affected: {', '.join(ticker_info['affected_positively'])}")
            if ticker_info["affected_negatively"]:
                print(f"  Negatively affected: {', '.join(ticker_info['affected_negatively'])}")
        else:
            print("Tickers: None identified")
        
        print("-" * 50)

        self.all_articles.append({
            "title": title,
            "sentiment": sentiment_result['label'].upper(),
            "score": sentiment_result['score'],
            "signal": sentiment_result['signal'],
            "tickers": [t.ticker for t in ticker_info["tickers"]],
            "primary_ticker": ticker_info["primary_ticker"],
            "ticker_impacts": [
                {
                    "ticker": t.ticker,
                    "impact": t.impact,
                    "relevance": t.relevance,
                } for t in ticker_info["tickers"]
            ]
        })