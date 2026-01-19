import re
from typing import Optional
from dataclasses import dataclass

@dataclass
class TickerImpact:
    ticker: str
    relevance: str  # "high" (in title) or "medium" (in description only)
    impact: str     # "positive", "negative", or "neutral"


class TickerExtractor:

    COMPANY_TICKERS = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "meta": "META",
        "facebook": "META",
        "netflix": "NFLX",
        "walmart": "WMT",
        "jpmorgan": "JPM",
        "jp morgan": "JPM",
        "goldman sachs": "GS",
        "bank of america": "BAC",
        "boeing": "BA",
        "disney": "DIS",
        "coca-cola": "KO",
        "coca cola": "KO",
        "pepsi": "PEP",
        "pepsico": "PEP",
        "intel": "INTC",
        "amd": "AMD",
        "salesforce": "CRM",
        "adobe": "ADBE",
        "paypal": "PYPL",
        "uber": "UBER",
        "lyft": "LYFT",
        "airbnb": "ABNB",
        "zoom": "ZM",
        "spotify": "SPOT",
        "twitter": "X",
        "chevron": "CVX",
        "exxon": "XOM",
        "exxonmobil": "XOM",
    }
    
    TICKER_PATTERN = re.compile(r'[\$\(]([A-Z]{1,5})[\)\s\.,]')
    
    def __init__(self, custom_mappings: Optional[dict] = None):
        self.mappings = {**self.COMPANY_TICKERS}
        if custom_mappings:
            self.mappings.update(custom_mappings)
    
    def _extract(self, text: str) -> list[str]:
        tickers = set()
        text_lower = text.lower()
        
        explicit_matches = self.TICKER_PATTERN.findall(text)
        tickers.update(explicit_matches)
        
        for company, ticker in self.mappings.items():
            if company in text_lower:
                tickers.add(ticker)
        
        return list(tickers)
    
    def extract_with_context(self, title: str, description: str) -> list[dict]:
        results = []
        
        title_tickers = self._extract(title)
        desc_tickers = self._extract(description or "")
        
        for ticker in title_tickers:
            results.append({"ticker": ticker, "relevance": "high"})
        
        for ticker in desc_tickers:
            if ticker not in title_tickers:
                results.append({"ticker": ticker, "relevance": "medium"}) # or low
        
        return results

    def get_tickers_with_impact(
        self, 
        title: str, 
        description: str, 
        sentiment_label: str, 
    ) -> list[TickerImpact]:
        """
        Extract tickers from news content and associate them with sentiment impact.
        
        Args:
            title: Article title
            description: Article description
            sentiment_label: Sentiment label ("positive", "negative", "neutral")
            
        Returns:
            List of TickerImpact objects. Empty list if no tickers found.
        """
        ticker_contexts = self.extract_with_context(title, description)
        
        if not ticker_contexts:
            return []
        
        impact_mapping = {
            "positive": "positive",
            "negative": "negative",
            "neutral": "neutral"
        }
        impact = impact_mapping.get(sentiment_label.lower(), "neutral")
        
        results = []
        for ctx in ticker_contexts:
            results.append(TickerImpact(
                ticker=ctx["ticker"],
                relevance=ctx["relevance"],
                impact=impact,
            ))
        
        return results
    
    def fetch_data(self, ticker: str, period: str = "1y"):
        import yfinance as yf
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
        
    def fetch_multiple_data(self, tickers: list[str]):
        import yfinance as yf
        data = yf.download(tickers, start="2023-01-01", auto_adjust=False)
        
        if data is not None:
            return data['Adj Close']
        
        return


def get_tickers(
    content: str,
    sentiment_result: Optional[dict] = None,
    extractor: Optional[TickerExtractor] = None
) -> list[TickerImpact]:
    """
    Extract tickers from news content with sentiment impact.
    
    Args:
        content: The text content (can be title, description, or combined)
        sentiment_result: Optional dict with 'label' and 'score' keys from SentimentAnalyzer
        extractor: Optional TickerExtractor instance (creates new one if not provided)
        
    Returns:
        List of TickerImpact objects with ticker, relevance, impact, and confidence.
        Returns empty list if no tickers are found.
    """
    if extractor is None:
        extractor = TickerExtractor()
    
    raw_tickers = extractor._extract(content)
    
    if not raw_tickers:
        return []
    
    if sentiment_result:
        label = sentiment_result.get("label", "neutral").lower()
        impact = "positive" if label == "positive" else "negative" if label == "negative" else "neutral"
    else:
        impact = "unknown"
    
    results = []
    for ticker in raw_tickers:
        results.append(TickerImpact(
            ticker=ticker,
            relevance="medium",  # Can't determine without separate title/description
            impact=impact,
        ))
    
    return results


def get_tickers_sentiment(
    title: str,
    description: str,
    sentiment_result: Optional[dict] = None,
    extractor: Optional[TickerExtractor] = None
) -> dict:
    """
    Extract tickers with detailed information including relevance based on location.
    
    Args:
        title: Article title
        description: Article description  
        sentiment_result: Optional dict with 'label', 'score'
        extractor: Optional TickerExtractor instance
        
    Returns:
        Dict with:
            - 'tickers': List of TickerImpact objects
            - 'count': Number of tickers found
            - 'has_tickers': Boolean indicating if any tickers were found
            - 'primary_ticker': The most relevant ticker (from title) or None
            - 'affected_positively': List of tickers with positive impact
            - 'affected_negatively': List of tickers with negative impact
    """
    if extractor is None:
        extractor = TickerExtractor()
    
    if sentiment_result:
        label = sentiment_result.get("label", "neutral").lower()
    else:
        label = "neutral"
    
    ticker_impacts = extractor.get_tickers_with_impact(title, description, label)
    
    positive_tickers = [t.ticker for t in ticker_impacts if t.impact == "positive"]
    negative_tickers = [t.ticker for t in ticker_impacts if t.impact == "negative"]
    
    primary = None
    for t in ticker_impacts:
        if t.relevance == "high":
            primary = t.ticker
            break
    
    return {
        "tickers": ticker_impacts,
        "count": len(ticker_impacts),
        "has_tickers": len(ticker_impacts) > 0,
        "primary_ticker": primary,
        "affected_positively": positive_tickers,
        "affected_negatively": negative_tickers,
    }
