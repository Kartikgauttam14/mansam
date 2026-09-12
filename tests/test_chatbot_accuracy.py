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
            ("bold and confident", "en", lambda r: r.get("intent") != "out_of_domain" and len(r["productLinks"]) == 1),
            ("show me top 2 perfumes", "en", lambda r: len(r["productIds"]) == 2 and len(r["productLinks"]) == 2),
            ("show me top 5 perfumes", "en", lambda r: len(r["productIds"]) == 5),
            ("show me the type of perfume", "en", lambda r: r.get("intent") == "perfume_types" and "floral" in r["answer"].lower()),
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

    def test_product_notes_follow_up_does_not_become_catalogue(self):
        recommendation = server.make_answer("I need a perfume for my girlfriend", "en")
        context_ids = recommendation["productIds"][:3]
        follow_up = server.make_answer(
            "show me the notes on this perfume",
            "en",
            context_product_ids=context_ids,
            conversation=[
                {"role": "customer", "content": "I need a perfume for my girlfriend"},
                {"role": "assistant", "content": recommendation["answer"]},
            ],
            profile={"productIds": context_ids},
        )
        self.assertLessEqual(len(follow_up["productLinks"]), 1)
        self.assertEqual(len(follow_up["productLinks"]), 1)
        self.assertNotIn("I found 20 perfumes", follow_up["answer"])

    def test_notes_question_without_context_requests_product(self):
        result = server.make_answer("show me the notes on this perfume", "en")
        self.assertNotEqual(result.get("intent"), "perfume_list")

    def test_price_range_recommendation_uses_new_products(self):
        context = ["55"]
        result = server.make_answer(
            "Can you suggest me two perfumes in this price range?",
            "en",
            context_product_ids=context,
            profile={"productIds": context},
        )
        self.assertEqual(result["intent"], "price_range_recommendation")
        self.assertEqual(len(result["productIds"]), 2)
        self.assertTrue(set(result["productIds"]).isdisjoint(context))
        self.assertIn("AED", result["answer"])

    def test_price_range_recommendation_respects_requested_quantity(self):
        for count in (2, 4, 5, 6, 8, 10):
            with self.subTest(count=count):
                context = ["55"]
                result = server.make_answer(
                    f"Suggest me {count} perfumes in this price range",
                    "en",
                    context_product_ids=context,
                    profile={"productIds": context},
                )
                self.assertEqual(result["intent"], "price_range_recommendation")
                self.assertEqual(len(result["productIds"]), count)
                self.assertTrue(set(result["productIds"]).isdisjoint(context))

    def test_similarity_words_start_new_recommendation(self):
        context = ["55"]
        for phrase in ("same price", "similar price", "same category", "same type", "similar products"):
            with self.subTest(phrase=phrase):
                result = server.make_answer(
                    f"Suggest me 2 perfumes in the {phrase}",
                    "en",
                    context_product_ids=context,
                    profile={"productIds": context},
                )
                self.assertIn(result["intent"], {"price_range_recommendation", "similar_product_recommendation"})
                self.assertEqual(len(result["productIds"]), 2)
                self.assertTrue(set(result["productIds"]).isdisjoint(context))


if __name__ == "__main__":
    unittest.main()
