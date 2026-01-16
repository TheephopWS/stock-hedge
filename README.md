# Stock Hedge - News Sentiment Analysis for Stocks and Options trading

A Python-based system for analyzing financial news sentiment and calculating options hedging strategies using the Black-Scholes model. The project leverages AI-powered sentiment analysis (FinBERT) to classify market news as bullish or bearish signals.

## Overview

This repository combines financial news analysis with quantitative options pricing to support informed hedging decisions:

- **News Aggregation**: Fetches real-time business news from NewsAPI
- **Sentiment Analysis**: Uses FinBERT (financial domain pre-trained transformer) to analyze market sentiment
- **Ticker Extraction**: Identifies company tickers from news articles using pattern matching and company name mapping
- **Options Pricing**: Black-Scholes model implementation for call/put pricing and Greeks calculation
- **Delta Hedging**: Automated hedge position calculation based on option deltas

## Getting Started

### Prerequisites

- Python 3.8+
- NewsAPI key (get one at [newsapi.org](https://newsapi.org))

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   NEWSAPI_KEY=your_newsapi_key_here
   ```

### Running the Application

Execute the news sentiment analysis pipeline:

```bash
python src/pipeline/main.py
```

This will:
- Fetch the latest 100 business news articles
- Analyze sentiment for each article
- Classify articles as BULLISH, BEARISH, or NEUTRAL
- Display sentiment scores and signals
- Track cumulative bullish/bearish article counts


## Configuration

Edit `src/config/settings.py` to customize:
- `SENTIMENT_POSITIVE_THRESHOLD`: Minimum confidence for bullish signal (default: 0.7)
- `SENTIMENT_NEGATIVE_THRESHOLD`: Minimum confidence for bearish signal (default: 0.7)

## Contributing

This is an active project. Key areas for improvement:
- Ticker extraction accuracy (see TODO in `tickers.py`)
- Portfolio optimization algorithms
- Multi-asset hedging strategies
- Backtesting framework

---

**Disclaimer:** This software is for educational and research purposes only. Not financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.
