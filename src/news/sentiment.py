from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import time

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SENTIMENT_POSITIVE_THRESHOLD, SENTIMENT_NEGATIVE_THRESHOLD

class SentimentAnalyzer:
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        self.pipe = pipeline("text-classification", 
                             model=self.model,
                             tokenizer=self.tokenizer,
                             device=self.device)
        
        self.positive_threshold = SENTIMENT_POSITIVE_THRESHOLD
        self.negative_threshold = SENTIMENT_NEGATIVE_THRESHOLD
    
    def analyze(self, text: str) -> dict:
        result = self.pipe(text)[0]
        return {
            "label": result["label"].lower(),  # positive, negative, neutral
            "score": result["score"],
            "signal": self._get_signal(result)
        }
    
    def analyze_batch(self, texts: list[str]) -> list[dict]:
        results = self.pipe(texts, batch_size=16)
        return [
            {
                "label": r["label"].lower(),
                "score": r["score"],
                "signal": self._get_signal(r)
            }
            for r in results
        ]
    
    def _get_signal(self, result: dict) -> str:
        label = result["label"].lower()
        score = result["score"]
        
        if label == "positive" and score >= self.positive_threshold:
            return "BULLISH"
        elif label == "negative" and score >= self.negative_threshold:
            return "BEARISH"
        return "NEUTRAL"
    

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    sample_texts = [
        "The company's stock price soared after the successful product launch.",
        "Market uncertainty is causing investors to be cautious.",
        "Oracle Corp. has pushed back the completion dates for some of the data centers it’s developing for the artificial intelligence model developer OpenAI to 2028 from 2027, according to people familiar with the work. The delays are largely due to labor and material shortages, said the people, asking not to be identified discussing private schedules."
    ]

    start_time = time.time()

    for text in sample_texts:
        print(f"Text: {text}\nAnalysis: {analyzer.analyze(text)}\n")

    print(f"Time used: {time.time() - start_time} seconds")

    