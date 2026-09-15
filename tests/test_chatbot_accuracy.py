import unittest
from unittest.mock import patch

import server


class ChatbotAccuracyBenchmark(unittest.TestCase):
    def test_discovery_filters_size_gender_and_disliked_notes(self):
        products = [
            {"id": "wrong-size", "volume": "50ml", "gender": "Unisex", "notes": {"en": ["Rose"]}},
            {"id": "wrong-gender", "volume": "100ml", "gender": "Male", "notes": {"en": ["Rose"]}},
            {"id": "disliked", "volume": "100ml", "gender": "Unisex", "notes": {"en": ["Rose", "Oud"]}},
            {"id": "match", "volume": "100ml", "gender": "Unisex", "notes": {"en": ["Rose"]}},
        ]
        for product in products:
            product.update(name={"en": product["id"]}, productLine={"en": "Eau de Parfum 100ml"})
        profile = {"discovery": {"gender": "female", "notes": "rose but not oud", "sizeMl": 100}}
        with patch.object(server, "CATALOG_PRODUCTS", products):
            result = server.make_answer("100 ml", "en", profile=profile)
            self.assertEqual(result["productIds"], ["match"])
            missing = server.make_answer("20 ml", "en", profile=profile)
            self.assertEqual(missing["intent"], "discovery_no_match")
            self.assertEqual(missing["productLinks"], [])
            self.assertIn("20 ml", missing["answer"])

    def test_discovery_real_catalogue_sizes_and_arabic(self):
        for size in (3, 20, 50, 100):
            result = server.make_answer(f"{size} ml", "en", profile={"discovery": {
                "gender": "unisex", "notes": "musk", "sizeMl": size}})
            by_id = {str(p.get("id")): p for p in server.CATALOG_PRODUCTS}
            for product_id in result["productIds"]:
                self.assertEqual(by_id[product_id]["volume"].lower(), f"{size}ml")
                self.assertEqual(by_id[product_id]["gender"].lower(), "unisex")
        result = server.make_answer("١٠٠ مل", "ar", profile={"discovery": {
            "gender": "unisex", "notes": "مسك", "sizeMl": 100}})
        self.assertEqual(result["intent"], "discovery_recommendation")
        self.assertEqual(result["language"], "ar")

    def test_single_gift_perfume_is_not_a_catalogue(self):
        for question in ("now show me a perfume for the gift", "show me one perfume for a gift", "give me a fragrance for a present"):
            for profile in ({}, {"preferences": ["rose"], "productIds": ["49"]}):
                with self.subTest(question=question, profile=profile):
                    result = server.make_answer(question, "en", profile=profile)
                    self.assertNotEqual(result.get("intent"), "perfume_list")
                    self.assertEqual(len(result["productLinks"]), 1)
                    self.assertEqual(len(result["productIds"]), 1)
                    self.assertIn("For a gift, I recommend", result["answer"])
                    self.assertNotIn("I found 20", result["answer"])

    def test_explicit_catalogue_request_is_preserved(self):
        self.assertTrue(server.is_perfume_list_request("show me all perfumes for a gift"))
        self.assertTrue(server.is_perfume_list_request("show me a list of perfumes"))
        self.assertFalse(server.is_perfume_list_request("show me a perfume"))

    def test_category_request_returns_two_products_without_workbook_dump(self):
        for product_id in ("55", "118"):
            with self.subTest(product_id=product_id):
                result = server.make_answer("Show me the 2 perfumes in this category.", "en",
                                            context_product_ids=[product_id])
                self.assertEqual(result["intent"], "category_recommendation")
                self.assertEqual(len(set(result["productIds"])), 2)
                self.assertEqual(len(result["productLinks"]), 2)
                by_id = {str(p.get("id")): p for p in server.CATALOG_PRODUCTS}
                for selected in result["productIds"]:
                    self.assertEqual(by_id[selected]["productLine"], by_id[product_id]["productLine"])
                self.assertNotIn("workbook", result["answer"])
                self.assertNotIn("24_Category_Purpose", result["answer"])
                self.assertIn("\n1. ", result["answer"])
                self.assertIn("\n2. ", result["answer"])

    def test_category_request_without_valid_context_asks_for_category(self):
        for context in ([], ["missing-product"]):
            result = server.make_answer("Show me the 2 perfumes in this category.", "en",
                                        context_product_ids=context)
            self.assertEqual(result["intent"], "category_clarification")
            self.assertEqual(result["productLinks"], [])
            self.assertNotIn("workbook", result["answer"])

    def test_two_perfumes_like_ghumud(self):
        for question in ("show me the 2 perfume like this", "give me two perfumes like that", "show me 2 similar fragrances"):
            with self.subTest(question=question):
                result = server.make_answer(
                    question, "en", context_product_ids=["118"],
                    conversation=[{"role": "customer", "text": "musk"}],
                    profile={"productIds": ["118"]},
                )
                self.assertEqual(result["intent"], "similar_product_recommendation")
                self.assertEqual(len(set(result["productIds"])), 2)
                self.assertEqual(len(result["productLinks"]), 2)
                self.assertNotIn("118", result["productIds"])
                self.assertIn("GHUMUD", result["answer"])

    def test_similar_perfumes_prioritize_preferred_shared_notes(self):
        def product(product_id, notes):
            return {"id": product_id, "name": {"en": product_id},
                    "productLine": {"en": "Eau de Parfum 100ml"},
                    "notes": {"en": notes}, "price": 100}
        products = [product("reference", ["Musk", "Rose"]),
                    product("unrelated", ["Oud"]), product("rose", ["Rose"]),
                    product("musk", ["Musk"]), product("both", ["Musk", "Rose"])]
        with patch.object(server, "CATALOG_PRODUCTS", products):
            result = server.make_answer(
                "show me the 2 perfume like this", "en", context_product_ids=["reference"],
                conversation=[{"role": "customer", "text": "musk"}],
            )
        self.assertEqual(result["productIds"], ["both", "musk"])

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
        for phrase in ("same price", "similar price", "same category", "same type", "similar products", "similar to this product"):
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
