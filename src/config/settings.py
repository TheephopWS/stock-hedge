from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://newsapi.org/v2/"
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

SENTIMENT_POSITIVE_THRESHOLD = 0.5
SENTIMENT_NEGATIVE_THRESHOLD = 0.5

if __name__ == "__main__":
    print(NEWSAPI_KEY)