"""Create a deterministic 80/20 split and evaluate general-chat intent routing."""

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from intent_classifier import IntentClassifier, normalize, phrase_matches


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_FILE = PROJECT_ROOT / "data" / "general-chat-intents.json"
GENERAL_QA_FILE = PROJECT_ROOT / "general_qa_intents.json"
TRAIN_FILE = PROJECT_ROOT / "data" / "general-chat-intents.train.json"
TEST_FILE = PROJECT_ROOT / "data" / "general-chat-intents.test.json"
REPORT_FILE = PROJECT_ROOT / "reports" / "general-intents-evaluation.json"
MARKDOWN_REPORT_FILE = PROJECT_ROOT / "reports" / "general-intents-evaluation.md"
SEED = 42
TEST_RATIO = 0.20


def load_general_qa_intents():
    source = json.loads(GENERAL_QA_FILE.read_text(encoding="utf-8"))
    intents = []
    for item in source.get("intents", []):
        tag = str(item.get("tag", "")).strip().lower()
        patterns = [str(value).strip() for value in item.get("patterns", []) if str(value).strip()]
        responses = [str(value).strip() for value in item.get("responses", []) if str(value).strip()]
        if not tag or tag == "fallback" or not patterns or not responses:
            continue
        if tag == "greeting":
            responses = ["Hello! How are you today?"]
        intents.append({
            "id": f"qa_{tag}",
            "examples": {"en": patterns},
            "response": {"en": responses[0], "ar": ""},
        })
    return intents


def flatten_examples(intents):
    examples = []
    for intent in intents:
        for language, phrases in intent.get("examples", {}).items():
            for phrase in phrases:
                examples.append({"intent": intent["id"], "language": language, "text": phrase})
    return examples


def test_counts_by_intent(examples, target_test_count):
    counts = Counter(example["intent"] for example in examples)
    quotas = {intent: count * TEST_RATIO for intent, count in counts.items()}
    allocation = {intent: min(count - 1, math.floor(quota)) for intent, (count, quota) in {
        intent: (counts[intent], quotas[intent]) for intent in counts
    }.items()}
    remaining = target_test_count - sum(allocation.values())
    for intent in sorted(counts, key=lambda item: (quotas[item] - allocation[item], counts[item]), reverse=True):
        if remaining <= 0:
            break
        if allocation[intent] < counts[intent] - 1:
            allocation[intent] += 1
            remaining -= 1
    return allocation


def split_examples(examples):
    rng = random.Random(SEED)
    target_test_count = round(len(examples) * TEST_RATIO)
    per_intent_test_count = test_counts_by_intent(examples, target_test_count)
    groups = defaultdict(list)
    for example in examples:
        groups[example["intent"]].append(example)

    train, test = [], []
    for intent in sorted(groups):
        group = groups[intent]
        # Shuffle within each intent so every split can represent both languages.
        rng.shuffle(group)
        selected = []
        languages = sorted({example["language"] for example in group})
        for language in languages:
            if len(selected) >= per_intent_test_count[intent]:
                break
            candidate = next((example for example in group if example["language"] == language), None)
            if candidate:
                selected.append(candidate)
        for example in group:
            if len(selected) >= per_intent_test_count[intent]:
                break
            if example not in selected:
                selected.append(example)
        test.extend(selected)
        train.extend(example for example in group if example not in selected)
    return train, test


def make_intent_file(source_intents, examples):
    examples_by_intent = defaultdict(lambda: defaultdict(list))
    for example in examples:
        examples_by_intent[example["intent"]][example["language"]].append(example["text"])
    return {
        "split": {
            "seed": SEED,
            "testRatio": TEST_RATIO,
            "purpose": "General-chat intent training/evaluation only. Product recommendations remain in the RAG catalogue.",
        },
        "intents": [
            {
                "id": intent["id"],
                "examples": {
                    language: examples_by_intent[intent["id"]][language]
                    for language in ("en", "ar")
                    if examples_by_intent[intent["id"]][language]
                },
                "response": intent["response"],
            }
            for intent in source_intents
        ],
    }


def predict_intent(message, train_intents, classifier=None):
    # Direct phrase routes remain the preferred production behavior.
    matched_intent = None
    matched_length = 0
    for intent in train_intents:
        for phrases in intent.get("examples", {}).values():
            for phrase in phrases:
                if phrase_matches(message, phrase) and len(normalize(phrase)) > matched_length:
                    matched_intent = intent["id"]
                    matched_length = len(normalize(phrase))
    if matched_intent:
        return matched_intent
    return (classifier or IntentClassifier(train_intents)).predict(message)


def evaluate(test_examples, train_intents):
    classifier = IntentClassifier(train_intents)
    rows = []
    for example in test_examples:
        predicted = predict_intent(example["text"], train_intents, classifier)
        rows.append({
            **example,
            "predictedIntent": predicted,
            "passed": predicted == example["intent"],
        })
    return rows


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(rows, full_corpus_rows, total_examples, train_count):
    passed = sum(row["passed"] for row in rows)
    accuracy = (passed / len(rows) * 100) if rows else 0
    full_corpus_passed = sum(row["passed"] for row in full_corpus_rows)
    full_corpus_accuracy = (full_corpus_passed / len(full_corpus_rows) * 100) if full_corpus_rows else 0
    lines = [
        "# General Intent Train/Test Evaluation",
        "",
        f"- Source examples: {total_examples}",
        f"- Training examples: {train_count} (80%)",
        f"- Holdout test examples: {len(rows)} (20%)",
        f"- Split seed: {SEED}",
        f"- Intent-routing accuracy: {accuracy:.1f}% ({passed}/{len(rows)})",
        f"- Full-corpus regression routing: {full_corpus_accuracy:.1f}% ({full_corpus_passed}/{len(full_corpus_rows)})",
        "",
        "The holdout result evaluates routing with only the training examples loaded. The full-corpus result is a regression check for the production intent file, not a second holdout score.",
        "",
        "| Language | Question | Expected intent | Predicted intent | Result |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        result = "PASS" if row["passed"] else "FAIL"
        predicted = row["predictedIntent"] or "unmatched"
        lines.append(f"| {row['language']} | {row['text']} | {row['intent']} | {predicted} | {result} |")
    MARKDOWN_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Split and test Mansam general-chat intents.")
    parser.add_argument("--check", action="store_true", help="Fail when holdout accuracy is below the accepted threshold.")
    parser.add_argument("--minimum-accuracy", type=float, default=0.70, help="Minimum accuracy required by --check (default: 0.70).")
    args = parser.parse_args()

    source = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    source_intents = load_general_qa_intents() + source.get("intents", [])
    examples = flatten_examples(source_intents)
    train_examples, test_examples = split_examples(examples)
    train_payload = make_intent_file(source_intents, train_examples)
    test_payload = make_intent_file(source_intents, test_examples)
    rows = evaluate(test_examples, train_payload["intents"])
    full_corpus_rows = evaluate(examples, source_intents)
    passed = sum(row["passed"] for row in rows)
    accuracy = (passed / len(rows)) if rows else 0
    full_corpus_passed = sum(row["passed"] for row in full_corpus_rows)
    full_corpus_accuracy = (full_corpus_passed / len(full_corpus_rows)) if full_corpus_rows else 0

    write_json(TRAIN_FILE, train_payload)
    write_json(TEST_FILE, test_payload)
    write_json(REPORT_FILE, {
        "sourceExamples": len(examples),
        "trainExamples": len(train_examples),
        "testExamples": len(test_examples),
        "trainRatio": round(len(train_examples) / len(examples), 4) if examples else 0,
        "testRatio": round(len(test_examples) / len(examples), 4) if examples else 0,
        "seed": SEED,
        "accuracy": round(accuracy, 4),
        "passed": passed,
        "failed": len(rows) - passed,
        "fullCorpusRegressionAccuracy": round(full_corpus_accuracy, 4),
        "fullCorpusRegressionPassed": full_corpus_passed,
        "fullCorpusRegressionFailed": len(full_corpus_rows) - full_corpus_passed,
        "results": rows,
    })
    write_markdown(rows, full_corpus_rows, len(examples), len(train_examples))

    print(f"Created {len(train_examples)} training and {len(test_examples)} test examples.")
    print(f"Holdout accuracy: {accuracy:.1%} ({passed}/{len(rows)})")
    print(f"Full-corpus regression routing: {full_corpus_accuracy:.1%} ({full_corpus_passed}/{len(full_corpus_rows)})")
    print(f"Report: {MARKDOWN_REPORT_FILE}")
    if args.check and accuracy < args.minimum_accuracy:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
