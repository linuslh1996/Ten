from typing import List

from textblob import TextBlob


def choose_best_review(reviews: List[str]) -> str:
    reviews_with_good_length: List[str] = [review for review in reviews if len(review) > 250 and len(review) < 1000]
    reviews_with_good_length = sorted(reviews_with_good_length, key=_get_sentiment)
    return reviews_with_good_length[0]


def _get_sentiment(review: str) -> float:
    blob: TextBlob = TextBlob(review)
    return abs(blob.polarity)