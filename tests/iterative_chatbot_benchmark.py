import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
import server


def make_round(prefix):
    if prefix == 2:
        questions = [
            ("Hello, I am back", "greeting"), ("Hi, good morning", "greeting"), ("Hey there", "greeting"),
            ("Good day to you", "greeting"), ("Hello, nice to see you", "greeting"), ("I am okay today", "wellbeing"),
            ("I am feeling good", "wellbeing"), ("Doing fine, thanks", "wellbeing"), ("I feel awesome", "wellbeing"),
            ("Thanks a lot", "thanks"), ("That helped me", "thanks"), ("Who are you?", "general"),
            ("What can you help me with?", "general"), ("I want a perfume for my aunt", "recommend"),
            ("Find a scent for my daughter", "recommend"), ("I need one for my son", "recommend"),
            ("Suggest something for my sister-in-law", "recommend"), ("I want a gift for my partner", "recommend"),
            ("Find a fragrance for a gentleman", "recommend"), ("I need something for a young woman", "recommend"),
            ("Show me a fragrance for a young man", "recommend"), ("I am shopping for myself", "recommend"),
            ("Find me something for a special occasion", "recommend"), ("Recommend a signature scent", "recommend"),
            ("I want a clean office scent", "recommend"), ("Find a citrus fragrance", "recommend"),
            ("I want a perfume with musk", "recommend"), ("Suggest a fruity perfume", "recommend"),
            ("I want a smoky scent", "recommend"), ("Find something elegant and powerful", "recommend"),
            ("I want a perfume for spring", "recommend"), ("Suggest something for a cold evening", "recommend"),
            ("I like amber and saffron", "recommend"), ("I prefer leather notes", "recommend"),
            ("What fragrance families do you offer?", "types"), ("What are your perfume formats?", "types"),
            ("Which fragrance styles can I choose from?", "types"), ("Do you have perfume categories?", "types"),
            ("What kind of scent is available?", "types"), ("List the perfume options", "list"),
            ("Show me the top 1 perfume", "list"), ("Give me the top 4 perfumes", "list"),
            ("Show me the top 6 perfumes", "list"), ("Give me the top 8 perfumes", "list"),
            ("List all women's fragrances", "list"), ("List all men's fragrances", "list"),
            ("Show me the attar products", "list"), ("Show me the home scents", "list"),
            ("What are the notes in Tahta Al Noujoum?", "details"), ("Tell me the notes of Qublat Ward", "details"),
            ("What ingredients does Al Shaghaf Al Ahmar have?", "details"), ("How does Mamlakati smell?", "details"),
            ("Tell me about Hadeeth Al Rooh", "details"), ("How much is Tahta Al Noujoum?", "price"),
            ("What is the cost of Qublat Ward?", "price"), ("Show the price for Hadeeth Al Rooh", "price"),
            ("Is Al Shaghaf Al Ahmar available?", "availability"), ("Do you have Qublat Ward in stock?", "availability"),
            ("Compare Tahta Al Noujoum and Qublat Ward", "compare"), ("Which is better, Hamsa or Mamlakati?", "compare"),
            ("Compare Hadeeth Al Rooh with Al Shaghaf Al Ahmar", "compare"), ("Where is the Mansam shop?", "website"),
            ("Can I get a link to the Mansam catalogue?", "website"), ("How do I buy a Mansam perfume?", "website"),
            ("I need a bold scent for my wife", "recommend"), ("Find an oud scent for my husband", "recommend"),
            ("Suggest floral notes for my mother", "recommend"), ("I want something sweet for my girlfriend", "recommend"),
            ("Find a woody gift for my boyfriend", "recommend"), ("Recommend something warm for my father", "recommend"),
            ("I want a romantic rose fragrance", "recommend"), ("Find a fresh summer scent for her", "recommend"),
            ("Suggest a strong winter scent for him", "recommend"), ("I want something with vanilla and musk", "recommend"),
            ("Tell me about this perfume", "context_details"), ("Show the notes for this one", "context_details"),
            ("How much does this one cost?", "context_price"), ("Is this one available?", "context_availability"),
            ("Give me another option for a woman", "context_recommend"), ("I changed it to a man", "context_recommend"),
            ("Which Mansam perfume has oud?", "recommend"), ("Which one has jasmine?", "recommend"),
            ("Do you sell rose perfumes?", "recommend"), ("Do you have a daily fragrance?", "recommend"),
            ("What is your best floral perfume?", "recommend"), ("What is your best oud perfume?", "recommend"),
            ("Can you help me choose a fragrance?", "recommend"), ("I need a perfume recommendation", "recommend"),
            ("Tell me about Mansam products", "types"), ("What does Mansam offer?", "types"),
            ("Can you show product links?", "website"), ("Does Mansam have delivery?", "website"),
            ("Please recommend a perfume for a gift", "recommend"), ("I want a fragrance that feels confident", "recommend"),
            ("I need a refined perfume for dinner", "recommend"), ("Find a light scent for daytime", "recommend"),
        ]
    else:
        questions = [
            ("Hello again, my name is Alex", "greeting"), ("Good morning, friend", "greeting"),
            ("I am doing great, thank you", "wellbeing"), ("I am fine today", "wellbeing"),
            ("Thanks, that is useful", "thanks"), ("What do you do?", "general"),
            ("Recommend something for my cousin", "recommend"), ("I need one for my grandmother", "recommend"),
            ("Find one for my colleague", "recommend"), ("I want one for my fiancée", "recommend"),
            ("Suggest a fragrance for a birthday gift", "recommend"), ("I need an everyday scent", "recommend"),
            ("Find a bright citrus scent", "recommend"), ("I want a deep oud perfume", "recommend"),
            ("Suggest a creamy floral scent", "recommend"), ("I like spicy amber fragrances", "recommend"),
            ("I want a sweet vanilla perfume", "recommend"), ("Find a confident perfume", "recommend"),
            ("I prefer soft rose notes", "recommend"), ("Give me the perfume types", "types"),
            ("What kinds of Mansam scent are there?", "types"), ("Show every perfume", "list"),
            ("Show me top 7 perfumes", "list"), ("Give me top 9 perfumes", "list"),
            ("List women's products", "list"), ("List men's products", "list"),
            ("What notes are in Aala Sathi Al Qamar?", "details"), ("What does Sarhan contain?", "details"),
            ("Tell me the price of Hamsa", "price"), ("Is Mamlakati available now?", "availability"),
            ("Compare Sarhan and Hamsa", "compare"), ("Where can I view Mansam online?", "website"),
            ("Can I have the link for Sarhan?", "website"), ("What is in the live catalogue?", "types"),
            ("I need a perfume for my partner", "recommend"), ("Find something for my parent", "recommend"),
            ("Give me a bold masculine fragrance", "recommend"), ("Find a feminine floral fragrance", "recommend"),
            ("I want a warm perfume for autumn", "recommend"), ("Suggest a cool scent for summer", "recommend"),
            ("Find a long-lasting woody fragrance", "recommend"), ("Recommend an elegant musk scent", "recommend"),
            ("I want rose, vanilla, and oud", "recommend"), ("Find a perfume for a wedding", "recommend"),
            ("Show me notes for this fragrance", "context_details"), ("What is the price of this one?", "context_price"),
            ("Is this available in the catalogue?", "context_availability"), ("Suggest another for her", "context_recommend"),
            ("Now make it for him", "context_recommend"), ("Which perfume should I try first?", "recommend"),
            ("Can you guide me to a Mansam scent?", "recommend"), ("I want to explore fragrances", "recommend"),
            ("Do you have attars?", "list"), ("Do you have bukhoor?", "list"),
            ("Do you have candles?", "list"), ("Do you have diffusers?", "list"),
            ("What is the difference between oud and floral?", "types"), ("Can I compare two products?", "compare"),
            ("Show me the notes in Al Shawk", "details"), ("How much is Mamlakati in AED?", "price"),
            ("Is Al Shawk in stock?", "availability"), ("I need help with a Mansam order", "website"),
            ("I want a present for my wife", "recommend"), ("I want a present for my husband", "recommend"),
            ("Find a fresh perfume for myself", "recommend"), ("Suggest a romantic scent for her", "recommend"),
            ("Find a powerful scent for him", "recommend"), ("Show me the catalogue categories", "types"),
            ("What is a good daily fragrance?", "recommend"), ("What is a good evening fragrance?", "recommend"),
            ("I like clean and modern scents", "recommend"), ("I like rich and luxurious scents", "recommend"),
            ("Tell me about the Mansam brand", "website"), ("How can I find a product page?", "website"),
            ("Suggest a perfume and include its link", "recommend"), ("I want to see a fragrance price", "price"),
            ("Which scent is suitable for a confident person?", "recommend"), ("Help me choose between floral and oud", "types"),
        ]
    questions += [
        ("Suggest a Mansam perfume with oud", "recommend"),
        ("Show me a floral scent for a gift", "recommend"),
        ("What notes does Al Shawk have?", "details"),
        ("What is the price of Sarhan?", "price"),
        ("Find a perfume with a clean modern character", "recommend"),
        ("Suggest a fragrance for a graduation gift", "recommend"),
        ("I want a deep incense scent", "recommend"),
        ("Recommend something with leather and amber", "recommend"),
        ("Show me a scent for a summer morning", "recommend"),
        ("Give me a perfume for my grandmother", "recommend"),
        ("I need one for my colleague", "recommend"),
        ("What is a good scent for a date night?", "recommend"),
        ("Show me a perfume with sandalwood", "recommend"),
        ("I want a fruity floral fragrance", "recommend"),
        ("What are the notes in Aala Sathi Al Qamar?", "details"),
        ("How much is Qublat Ward?", "price"),
        ("Is Hadeeth Al Rooh available?", "availability"),
        ("Compare Sarhan with Qublat Ward", "compare"),
        ("Show me the Mansam perfume categories", "types"),
        ("Can you recommend a perfume with a memorable trail?", "recommend"),
        ("Where can I shop for Mansam fragrances?", "website"),
        ("Tell me about perfume gifts", "recommend"),
    ]
    return [{"q": q, "kind": kind, "context": ["48"] if kind.startswith("context_") else []} for q, kind in questions[:100]]


MIXED_50 = [
    {"q":"Which Mansam perfume has rose and oud?","kind":"related"},
    {"q":"I need a fresh perfume for my sister","kind":"related"},
    {"q":"Show me top 3 women's perfumes","kind":"related"},
    {"q":"What are the notes in Sarhan?","kind":"related"},
    {"q":"Compare Mamlakati with Sarhan","kind":"related"},
    {"q":"Which fragrance suits a bold, warm, romantic evening gift for my wife?","kind":"hard"},
    {"q":"I changed from a floral perfume for my girlfriend to an oud one for my father; suggest one","kind":"hard"},
    {"q":"Show me the notes and price of the perfume you just recommended","kind":"hard","context":["48"]},
    {"q":"Give me the top 5 available products for a confident man with woody notes","kind":"hard"},
    {"q":"What is the difference between a daily fresh scent and a warm spicy evening scent?","kind":"hard"},
    {"q":"What is the capital of France?","kind":"negative"}, {"q":"Tell me a recipe for biryani","kind":"negative"},
    {"q":"Book me a hotel room","kind":"negative"}, {"q":"Who won yesterday's match?","kind":"negative"},
    {"q":"Explain quantum mechanics","kind":"negative"},
]
MIXED_50 += [{"q": f"{prefix} Mansam fragrance {style}", "kind":"normal"} for prefix, style in [
    ("Suggest a", "for a friend"), ("Find a", "with amber"), ("Show me a", "with jasmine"),
    ("I want a", "woody scent"), ("Recommend a", "sweet fragrance"), ("Find a", "romantic rose perfume"),
    ("Suggest a", "fresh office fragrance"), ("I need a", "gift for my mother"), ("Show me a", "masculine perfume"),
    ("Find a", "feminine perfume"), ("I want a", "winter scent"), ("Recommend a", "summer fragrance"),
    ("Suggest a", "bold perfume"), ("Find a", "soft floral scent"), ("I need a", "daily fragrance"),
    ("Show me a", "luxurious oud scent"), ("Recommend a", "musk perfume"), ("Find a", "vanilla fragrance"),
    ("I want a", "scent for dinner"), ("Suggest a", "perfume for myself"),
    ("Show me the", "type of perfume"), ("Give me the", "perfume list"), ("Show me top 4", "perfumes"),
    ("What are the", "notes in Hamsa"), ("What is the", "price of Mamlakati"), ("Is", "Sarhan available"),
    ("Compare", "Hamsa and Sarhan"), ("Where is the", "Mansam catalogue"), ("Do you sell", "attars"),
    ("Do you have", "bukhoor"), ("Tell me the", "fragrance categories"),
    ("What are the", "Mansam perfume styles"), ("Show me", "perfume formats"),
    ("I need a", "fresh floral scent"), ("Recommend a", "warm oud perfume"),
]]


def valid(item, result):
    answer = str(result.get("answer", ""))
    lower = answer.lower()
    links = result.get("productLinks", [])
    kind = item["kind"]
    if kind == "negative":
        return result.get("intent") == "out_of_domain" and not links
    if kind in {"greeting", "wellbeing", "thanks", "general"}:
        return result.get("intent") not in {"out_of_domain", "perfume_list"} and "could not reach" not in lower
    if kind == "types":
        return result.get("intent") == "perfume_types" or any(word in lower for word in ("floral", "oud", "fresh", "woody", "attars"))
    if kind == "list":
        if result.get("intent") != "perfume_list": return False
        import re
        match = re.search(r"top\s+(\d+)", item["q"].lower())
        return not match or len(result.get("productIds", [])) == int(match.group(1))
    if kind == "compare": return result.get("intent") in {"comparison", "comparison_clarification"} and (len(links) >= 2 or result.get("intent") == "comparison_clarification")
    if kind in {"details", "context_details"}: return len(links) <= 1 and bool(answer)
    if kind in {"price", "context_price"}: return len(links) <= 1 and ("aed" in lower or "price" in lower or "cost" in lower)
    if kind == "availability" or kind == "context_availability": return len(links) <= 1 and any(word in lower for word in ("available", "stock", "listed"))
    if kind == "website": return bool(answer) and any(word in lower for word in ("mansam", "catalog", "website", "order", "link", "deliver"))
    if kind in {"recommend", "context_recommend", "related", "hard", "normal"}:
        return (bool(links) or result.get("intent") in {"perfume_types", "style_comparison"}) and result.get("intent") != "out_of_domain"
    return False


def run_round(name, items, retries=2):
    for attempt in range(1, retries + 2):
        failures = []
        for index, item in enumerate(items, 1):
            context = item.get("context", [])
            result = server.make_answer(item["q"], "en", context_product_ids=context, profile={"productIds": context})
            if not valid(item, result): failures.append((index, item, result))
        print(f"{name} attempt {attempt}: {len(items) - len(failures)}/{len(items)} passed")
        if not failures: return True
        print("First failure:", failures[0][0], failures[0][1]["q"], "=>", failures[0][2].get("answer", ""))
        # The next attempt intentionally starts at question 1 again.
    return False


def main():
    round_two = make_round(2)
    round_three = make_round(3)
    (Path(__file__).with_name("english_chatbot_round2_100.json")).write_text(json.dumps(round_two, indent=2), encoding="utf-8")
    (Path(__file__).with_name("english_chatbot_round3_100.json")).write_text(json.dumps(round_three, indent=2), encoding="utf-8")
    (Path(__file__).with_name("english_chatbot_mixed_50.json")).write_text(json.dumps(MIXED_50[:50], indent=2), encoding="utf-8")
    first = run_round("Round 1", round_two)
    if not first: return 1
    second = run_round("Round 2", round_three)
    if not second: return 1
    third = run_round("Mixed stress", MIXED_50[:50])
    return 0 if third else 1


if __name__ == "__main__":
    sys.exit(main())
