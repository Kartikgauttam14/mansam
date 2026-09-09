"""Dependency-free bilingual intent classifier for short, general chat messages."""

import math
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher


def normalize(text):
    value = (text or "").lower()
    value = value.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    value = value.replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"[\u064B-\u065F\u0670\u0640]", "", value)


def phrase_matches(message, example):
    normalized_message = normalize(message)
    normalized_example = normalize(example)
    if not normalized_example:
        return False
    if re.fullmatch(r"[a-z0-9 ]+", normalized_example):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalized_example)}(?![a-z0-9])", normalized_message))
    return normalized_example in normalized_message


def features(text):
    normalized = normalize(text)
    words = re.findall(r"[a-z0-9]+|[\u0600-\u06FF]+", normalized)
    values = {f"word:{word}" for word in words}
    compact = re.sub(r"\s+", " ", normalized).strip()
    for size in (2, 3, 4):
        for index in range(max(0, len(compact) - size + 1)):
            values.add(f"char:{compact[index:index + size]}")
    return values


def phrase_similarity(first, second):
    """Score related short phrases when an exact training phrase is absent."""
    first_normalized = normalize(first)
    second_normalized = normalize(second)
    first_words = set(re.findall(r"[a-z0-9]+|[\u0600-\u06FF]+", first_normalized))
    second_words = set(re.findall(r"[a-z0-9]+|[\u0600-\u06FF]+", second_normalized))
    word_score = (2 * len(first_words & second_words) / (len(first_words) + len(second_words))) if first_words or second_words else 0
    first_char_features = {value for value in features(first_normalized) if value.startswith("char:")}
    second_char_features = {value for value in features(second_normalized) if value.startswith("char:")}
    char_score = (2 * len(first_char_features & second_char_features) / (len(first_char_features) + len(second_char_features))) if first_char_features or second_char_features else 0
    sequence_score = SequenceMatcher(None, first_normalized, second_normalized).ratio()
    return (word_score * 0.50) + (char_score * 0.30) + (sequence_score * 0.20)


class IntentClassifier:
    """Multinomial Naive Bayes classifier trained from the intent examples."""

    def __init__(self, intents):
        self.document_counts = Counter()
        self.feature_counts = defaultdict(Counter)
        self.feature_totals = Counter()
        self.vocabulary = set()
        self.labels = []
        self.examples = []
        for intent in intents:
            label = intent["id"]
            self.labels.append(label)
            for phrases in intent.get("examples", {}).values():
                for phrase in phrases:
                    self.examples.append((label, phrase))
                    self.document_counts[label] += 1
                    for feature in features(phrase):
                        self.feature_counts[label][feature] += 1
                        self.feature_totals[label] += 1
                        self.vocabulary.add(feature)
        self.total_documents = sum(self.document_counts.values())

    def predict(self, message):
        message_features = features(message)
        if not message_features or not self.labels or not self.total_documents:
            return None
        closest_label = None
        closest_score = 0
        for label, phrase in self.examples:
            score = phrase_similarity(message, phrase)
            if score > closest_score:
                closest_label = label
                closest_score = score

        best_label = self._bayes_prediction(message_features)
        return closest_label if closest_score >= 0.44 else best_label

    def predict_with_similarity(self, message):
        """Return the best label plus phrase similarity for safe production routing."""
        message_features = features(message)
        if not message_features or not self.labels or not self.total_documents:
            return None, 0
        closest_label = None
        closest_score = 0
        for label, phrase in self.examples:
            score = phrase_similarity(message, phrase)
            if score > closest_score:
                closest_label = label
                closest_score = score
        return (closest_label if closest_score >= 0.44 else self._bayes_prediction(message_features), closest_score)

    def _bayes_prediction(self, message_features):
        vocabulary_size = max(1, len(self.vocabulary))
        best_label = None
        best_score = float("-inf")
        for label in self.labels:
            score = math.log(self.document_counts[label] / self.total_documents)
            denominator = self.feature_totals[label] + vocabulary_size
            for feature in message_features:
                score += math.log((self.feature_counts[label][feature] + 1) / denominator)
            if score > best_score:
                best_label = label
                best_score = score
        return best_label
