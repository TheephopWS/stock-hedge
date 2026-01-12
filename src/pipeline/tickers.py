import re
from typing import Optional

'''
Temporary tickers retrieval using regex and a predefined mapping.
TODO: Replace with a more robust solution, possibly integrating with a financial data API/ other machine learning model.
'''
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

        