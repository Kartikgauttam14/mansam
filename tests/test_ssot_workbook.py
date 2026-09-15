import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SsotWorkbookCoverage(unittest.TestCase):
    def test_every_workbook_sheet_is_exported_to_training(self):
        with (ROOT / "data" / "ssot-knowledge.json").open(encoding="utf-8") as file:
            knowledge = json.load(file)
        with (ROOT / "data" / "ssot-training.jsonl").open(encoding="utf-8") as file:
            training_rows = [json.loads(line) for line in file if line.strip()]

        self.assertEqual(knowledge["sourceSheetCount"], 26)
        self.assertEqual(len(knowledge["sheets"]), knowledge["sourceSheetCount"])
        self.assertEqual(len(training_rows), sum(len(rows) for rows in knowledge["sheets"].values()))
        self.assertEqual({row["input"]["sheet"] for row in training_rows}, set(knowledge["sheets"]))


if __name__ == "__main__":
    unittest.main()
