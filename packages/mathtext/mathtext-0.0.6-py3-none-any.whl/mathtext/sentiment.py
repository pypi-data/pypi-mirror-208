from transformers import pipeline

sentiment_model = pipeline(task="sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def sentiment(text):
    """ Compute sentiment (positive/negative: 0-1) """
    return sentiment_model(text.lower())
