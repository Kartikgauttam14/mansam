import unittest

import server


class ChatbotAccuracyBenchmark(unittest.TestCase):
    def check(self, question, language, assertion):
        result = server.make_answer(question, language)
        self.assertTrue(assertion(result), f"Unexpected response for: {question}\n{result}")

    def test_domain_and_conversation_cases(self):
        cases = [
            ("Hello", "en", lambda r: r["intent"] in ("greeting", "qa_greeting")),
            ("I am fine how about you", "en", lambda r: r["intent"] == "wellbeing_reply"),
            ("I need a perfume for my wife", "en", lambda r: "wife" in r["answer"].lower() and len(r["productLinks"]) == 1),
            ("I need a perfume for my boyfriend", "en", lambda r: "boyfriend" in r["answer"].lower()),
            ("show me top 2 perfumes", "en", lambda r: len(r["productIds"]) == 2 and len(r["productLinks"]) == 2),
            ("show me top 5 perfumes", "en", lambda r: len(r["productIds"]) == 5),
            ("give me the list of attars", "en", lambda r: len(r["productIds"]) == 8),
            ("give me the list of candles", "en", lambda r: len(r["productIds"]) == 4),
            ("give me the list of bukhoor", "en", lambda r: len(r["productIds"]) == 4),
            ("what are the notes in Al Shawk?", "en", lambda r: "Al Shawk" in r["answer"] and len(r["productLinks"]) >= 1),
            ("what is the price of Al Shawk?", "en", lambda r: "AED" in r["answer"]),
            ("what is the price of this perfume?", "en", lambda r: len(r["productIds"]) == 0),
            ("أريد عطراً لزوجتي", "ar", lambda r: "زوجتك" in r["answer"]),
            ("ما هو سعر العطار الشوق؟", "ar", lambda r: "السعر" in r["answer"] or "AED" in r["answer"]),
            ("ما هي عاصمة الهند؟", "ar", lambda r: r["intent"] == "out_of_domain" and not r["productLinks"]),
            ("What is the capital of India?", "en", lambda r: r["intent"] == "out_of_domain" and not r["productLinks"]),
            ("Tell me a joke", "en", lambda r: r["intent"] == "out_of_domain"),
        ]
        passed = 0
        for question, language, assertion in cases:
            self.check(question, language, assertion)
            passed += 1
        self.assertGreaterEqual(passed / len(cases), 0.95)


if __name__ == "__main__":
    unittest.main()
