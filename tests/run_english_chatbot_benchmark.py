import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import server


DATA_FILE = Path(__file__).with_name("english_chatbot_100_questions.json")


def check(item, result):
    answer = str(result.get("answer", ""))
    lower = answer.lower()
    links = result.get("productLinks", [])
    kind = item["kind"]
    if kind in {"greeting", "wellbeing", "thanks", "capability"}:
        return result.get("intent") not in {"out_of_domain", "perfume_list"} and not "could not reach" in lower
    if kind == "out_of_domain":
        return result.get("intent") == "out_of_domain" and not links
    if kind == "types":
        return result.get("intent") == "perfume_types" or any(word in lower for word in ("floral", "oud", "fresh", "woody"))
    if kind == "list":
        if result.get("intent") != "perfume_list":
            return False
        count = item.get("count")
        return count is None or len(result.get("productIds", [])) == count
    if kind == "compare":
        return result.get("intent") == "comparison" and len(links) >= 2
    if kind in {"details", "price", "availability"}:
        if len(links) > item.get("maxLinks", 1):
            return False
        if item.get("context") and not links:
            return False
        if kind == "price" and "AED" not in answer and "price" not in lower:
            return False
        if kind == "availability" and not any(word in lower for word in ("available", "stock", "listed")):
            return False
        return kind == "details" or True
    if kind == "website":
        return bool(links) or any(word in lower for word in ("catalogue", "catalog", "mansam", "order", "deliver"))
    if kind == "recommend":
        if not links or result.get("intent") == "out_of_domain":
            return False
        required = item.get("must")
        if required and required in {"girlfriend", "wife", "mother", "sister", "boyfriend", "husband", "father", "brother", "uncle"}:
            return required in lower or (required in {"girlfriend", "wife", "mother", "sister"} and "feminine" in lower) or (required in {"boyfriend", "husband", "father", "brother", "uncle"} and "masculine" in lower)
        if required:
            return required in lower or required in str(result.get("memory", {})).lower()
        return True
    return False


def run():
    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    failures = []
    for number, item in enumerate(items, 1):
        result = server.make_answer(
            item["q"],
            "en",
            context_product_ids=item.get("context", []),
            profile={"productIds": item.get("context", [])},
        )
        passed = check(item, result)
        print(f"{number:03d} {'PASS' if passed else 'FAIL'} | {item['q']}")
        if not passed:
            failures.append((number, item, result))
    print(f"RESULT: {len(items) - len(failures)}/{len(items)} passed")
    if failures:
        for number, item, result in failures:
            print(f"FAILURE {number}: {item['q']} => {result.get('answer', '')}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
