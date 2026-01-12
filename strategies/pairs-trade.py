
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.tickers import TickerExtractor
import pandas as pd

TICKERS = []

if __name__ == "__main__":
    TE = TickerExtractor()
    data = TE.fetch_multiple_data(TICKERS)

    print(data)