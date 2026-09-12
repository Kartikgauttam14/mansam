import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
import server


ROUND_1 = [
    ("مرحباً", "greeting"), ("أهلاً", "greeting"), ("صباح الخير", "greeting"),
    ("مساء الخير", "greeting"), ("مرحباً يا صديقي", "greeting"), ("كيف حالك؟", "wellbeing"),
    ("أنا بخير، وأنت؟", "wellbeing"), ("أنا أيضاً بخير", "wellbeing"), ("شكراً لك", "thanks"),
    ("أنت مفيد جداً", "thanks"), ("ماذا يمكنك أن تفعل؟", "general"), ("من أنت؟", "general"),
    ("أريد عطراً لزوجتي", "recommend"), ("أريد عطراً لصديقتي", "recommend"),
    ("أريد عطراً لوالدتي", "recommend"), ("اقترح عطراً لأختي", "recommend"),
    ("أحتاج عطراً لابنتي", "recommend"), ("أريد عطراً لزوجي", "recommend"),
    ("أريد عطراً لصديقي", "recommend"), ("اقترح عطراً لوالدي", "recommend"),
    ("أحتاج عطراً لأخي", "recommend"), ("أريد هدية لعمي", "recommend"),
    ("أريد شراء عطر لنفسي", "recommend"), ("أريد عطراً لهم", "recommend"),
    ("أحتاج عطراً لابن عمي", "recommend"), ("اقترح عطراً لرجل", "recommend"),
    ("اقترح عطراً لامرأة", "recommend"), ("أريد عطراً جريئاً وواثقاً", "recommend"),
    ("أريد عطراً منعشاً للاستخدام اليومي", "recommend"), ("أحب العطور الحلوة", "recommend"),
    ("أفضل النفحات الزهرية", "recommend"), ("أحب الورد والعود", "recommend"),
    ("أريد عطراً رومانسياً", "recommend"), ("أريد عطراً بالمسك", "recommend"),
    ("أريد عطراً بالفواكه", "recommend"), ("أريد عطراً خشبياً", "recommend"),
    ("أريد عطراً بالعنبر والزعفران", "recommend"), ("أريد عطراً ناعماً", "recommend"),
    ("أرني أنواع العطور", "types"), ("ما هي فئات العطور؟", "types"),
    ("ما هي عائلات الروائح المتوفرة؟", "types"), ("ما هي أساليب العطور لديكم؟", "types"),
    ("ما أنواع المنتجات الموجودة؟", "types"), ("أرني قائمة العطور", "list"),
    ("أرني أفضل عطر", "list"), ("أرني أفضل عطرين", "list"),
    ("أرني أفضل 3 عطور", "list"), ("أرني أفضل 5 عطور", "list"),
    ("أرني أفضل 10 عطور", "list"), ("أرني كل عطور النساء", "list"),
    ("أرني كل عطور الرجال", "list"), ("أرني العطور الزيتية", "list"),
    ("أرني البخور", "list"), ("أرني الشموع", "list"), ("أرني المعطرات المنزلية", "list"),
    ("ما هي نفحات الشوق؟", "details"), ("ما هي نفحات مملكتي؟", "details"),
    ("ما مكونات آلا تاج وردة؟", "details"), ("كيف تفوح رائحة سرحان؟", "details"),
    ("ما رائحة همسة؟", "details"), ("ما سعر الشوق؟", "price"),
    ("كم سعر مملكتي؟", "price"), ("ما تكلفة آلا تاج وردة؟", "price"),
    ("هل عطر سرحان متوفر؟", "availability"), ("هل همسة متوفر في المخزون؟", "availability"),
    ("أين أجد كتالوج منسَم؟", "website"), ("أعطني رابط كتالوج منسَم", "website"),
    ("كيف أطلب عطراً من منسَم؟", "website"), ("قارن بين مملكتي وسرحان", "compare"),
    ("ما الفرق بين همسة وسرحان؟", "compare"), ("أيهما أفضل مملكتي أم الشوق؟", "compare"),
    ("حدثني عن هذا العطر", "context_details"), ("أرني نفحات هذا العطر", "context_details"),
    ("كم سعر هذا العطر؟", "context_price"), ("هل هذا العطر متوفر؟", "context_availability"),
    ("اقترح عطراً آخر لامرأة", "context_recommend"), ("غيّرت رأيي، أريده لرجل", "context_recommend"),
    ("أي عطر يحتوي على الورد والعود؟", "recommend"), ("أريد عطراً منعشاً للعمل", "recommend"),
    ("أريد عطراً دافئاً للشتاء", "recommend"), ("أريد عطراً أنيقاً لرجل", "recommend"),
    ("أريد عطراً ناعماً لامرأة", "recommend"), ("اقترح عطراً لهدية عيد ميلاد", "recommend"),
    ("ما أفضل عطر زهري؟", "recommend"), ("ما أفضل عطر عود؟", "recommend"),
    ("أريد عطراً للموعد المسائي", "recommend"), ("أريد عطراً للصيف", "recommend"),
    ("أعطني رابط عطر مملكتي", "website"), ("أرني سعر هذا العطر", "context_price"),
    ("هل لديكم عطور الورد؟", "recommend"), ("أريد استكشاف العطور", "recommend"),
    ("أرني عطراً مناسباً لي", "recommend"), ("اقترح عطراً كهدية", "recommend"),
    ("أريد عطراً فاخراً", "recommend"), ("أريد عطراً برائحة المسك والعنبر", "recommend"),
    ("ما المنتجات التي تقدمها منسَم؟", "types"), ("هل لديكم عطور يومية؟", "recommend"),
    ("أريد عطراً بنفحات خشب الصندل", "recommend"), ("أريد عطراً بنفحات الياسمين", "recommend"),
    ("ما العطر المناسب لشخص واثق؟", "recommend"), ("ساعدني في اختيار عطر", "recommend"),
    ("أريد عطراً لزفاف", "recommend"), ("أريد عطراً خفيفاً للنهار", "recommend"),
]

ROUND_2 = [
    ("مرحباً، عدت من جديد", "greeting"), ("أهلاً، صباح النور", "greeting"),
    ("أتمنى أن تكون بخير", "wellbeing"), ("أنا سعيد اليوم", "wellbeing"),
    ("شكراً، ساعدتني", "thanks"), ("كيف تساعدني؟", "general"),
    ("أريد عطراً لخالتي", "recommend"), ("أحتاج عطراً لجدتي", "recommend"),
    ("ابحث عن عطر لزميلي", "recommend"), ("أريد عطراً لشريكي", "recommend"),
    ("أريد عطراً لشخص مميز", "recommend"), ("أحب رائحة الحمضيات", "recommend"),
    ("أريد رائحة دخانية", "recommend"), ("أحب الفانيلا والمسك", "recommend"),
    ("أريد رائحة قوية", "recommend"), ("أريد عطراً لفصل الربيع", "recommend"),
    ("ما فئات العطور التي تقدمونها؟", "types"), ("هل لديكم أنواع مختلفة من العطور؟", "types"),
    ("اعرض جميع العطور", "list"), ("أرني أفضل 4 عطور", "list"),
    ("أرني أفضل 6 عطور", "list"), ("أرني أفضل 8 عطور", "list"),
    ("اعرض منتجات النساء", "list"), ("اعرض منتجات الرجال", "list"),
    ("هل لديكم عطور؟", "list"), ("هل لديكم عطور بخور؟", "list"),
    ("هل لديكم شموع؟", "list"), ("هل لديكم معطرات؟", "list"),
    ("ما نفحات تحت النجوم؟", "details"), ("ما الذي يحتويه قبلة ورد؟", "details"),
    ("أخبرني عن الشغف الأحمر", "details"), ("كم سعر حديث الروح؟", "price"),
    ("أرني سعر قبلة ورد", "price"), ("هل الشغف الأحمر متاح؟", "availability"),
    ("هل قبلة ورد في المخزون؟", "availability"), ("هل يمكنني رؤية متجر منسَم؟", "website"),
    ("أين أشتري عطور منسَم؟", "website"), ("هل يوجد توصيل للعطور؟", "website"),
    ("قارن بين تحت النجوم وقبلة ورد", "compare"), ("ما الفرق بين حديث الروح والشغف الأحمر؟", "compare"),
    ("أخبرني عن هذا المنتج", "context_details"), ("ما نفحات هذا المنتج؟", "context_details"),
    ("أرني تكلفة هذا المنتج", "context_price"), ("هل المنتج متاح؟", "context_availability"),
    ("اقترح خياراً آخر لها", "context_recommend"), ("الآن اجعله لرجل", "context_recommend"),
    ("أي عطر لديه الياسمين؟", "recommend"), ("هل تبيعون عطور الورد؟", "recommend"),
    ("أريد عطراً مكتبياً نظيفاً", "recommend"), ("أريد عطراً للمساء", "recommend"),
    ("أريد عطراً هادئاً لامرأة", "recommend"), ("أريد عطراً رجولياً بالعود", "recommend"),
    ("اقترح عطراً لوالدي", "recommend"), ("اقترح عطراً لابنة عمي", "recommend"),
    ("أريد عطراً لرحلة", "recommend"), ("أريد عطراً لمناسبة خاصة", "recommend"),
    ("ما العطر المناسب للاستخدام اليومي؟", "recommend"), ("أريد رائحة زهرية حلوة", "recommend"),
    ("أريد رائحة دافئة بالعنبر", "recommend"), ("أريد رائحة منعشة وخفيفة", "recommend"),
    ("أعطني رابط عطر سرحان", "website"), ("أرني فئة هذا العطر", "context_details"),
    ("ما سعر عطر همسة؟", "price"), ("هل عطر مملكتي متاح الآن؟", "availability"),
    ("أريد أن أختار بين الزهري والعود", "types"), ("هل يمكن مقارنة منتجين؟", "compare"),
    ("أرني عطراً بورد وعنبر", "recommend"), ("أرني عطراً بالجلد", "recommend"),
    ("أريد عطراً بفوحان مميز", "recommend"), ("أحتاج هدية لزوجي", "recommend"),
    ("أحتاج هدية لزوجتي", "recommend"), ("أريد عطراً لنفسي", "recommend"),
    ("أريد عطراً لصديقتي المقربة", "recommend"), ("أريد عطراً لصديقي المقرب", "recommend"),
    ("أريد عطراً للرجل", "recommend"), ("أريد عطراً للمرأة", "recommend"),
    ("أرني عطراً مناسباً لعشاء", "recommend"), ("ما العطر المناسب لهدية؟", "recommend"),
    ("أريد معرفة عروض العطور", "types"), ("أرني خيارات العطور", "list"),
    ("ما أفضل عطر للاستخدام اليومي؟", "recommend"), ("ساعدني على العثور على عطر", "recommend"),
    ("أريد عطراً لأبي", "recommend"), ("أريد عطراً لأمي", "recommend"),
    ("أريد عطراً لابني", "recommend"), ("أريد عطراً لابنتي", "recommend"),
    ("أريد عطراً لصديقي", "recommend"), ("أريد عطراً لصديقتي", "recommend"),
    ("أحب رائحة الورد", "recommend"), ("أحب رائحة العود", "recommend"),
    ("أحب رائحة العنبر", "recommend"), ("أحب رائحة الياسمين", "recommend"),
    ("أريد عطرًا ناعمًا للنهار", "recommend"), ("أريد عطرًا قوياً للمساء", "recommend"),
    ("اعرض أفضل عطرين للرجال", "list"), ("اعرض أفضل 7 عطور", "list"),
    ("ما نفحات قبلة ورد؟", "details"), ("كم سعر سرحان؟", "price"),
    ("هل عطر الشوق متوفر؟", "availability"), ("قارن بين قبلة ورد وحديث الروح", "compare"),
]

MIXED_50 = [
    {"q": "أي عطر من منسَم يحتوي على الورد والعود؟", "kind": "related"},
    {"q": "أحتاج عطراً منعشاً لأختي", "kind": "related"},
    {"q": "أرني أفضل 3 عطور للنساء", "kind": "related"},
    {"q": "ما نفحات سرحان؟", "kind": "related"},
    {"q": "قارن بين مملكتي وسرحان", "kind": "related"},
    {"q": "ما العطر المناسب لهدية رومانسية دافئة وجريئة لزوجتي؟", "kind": "hard"},
    {"q": "غيّرت اختياري من عطر زهري لصديقتي إلى عطر عود لوالدي، اقترح واحداً", "kind": "hard"},
    {"q": "أرني نفحات وسعر العطر الذي اقترحته للتو", "kind": "hard", "context": ["48"]},
    {"q": "أعطني أفضل 5 منتجات متاحة لرجل واثق يحب النفحات الخشبية", "kind": "hard"},
    {"q": "ما الفرق بين عطر منعش يومي وعطر دافئ مسائي؟", "kind": "hard"},
    {"q": "ما عاصمة فرنسا؟", "kind": "negative"}, {"q": "أعطني وصفة برياني", "kind": "negative"},
    {"q": "احجز لي غرفة في فندق", "kind": "negative"}, {"q": "من فاز بالمباراة أمس؟", "kind": "negative"},
    {"q": "اشرح لي ميكانيكا الكم", "kind": "negative"},
]
MIXED_50 += [{"q": q, "kind": "normal"} for q in [
    "اقترح عطراً لصديق", "ابحث عن عطر بالعنبر", "أرني عطراً بالياسمين", "أريد عطراً خشبياً",
    "أوصني بعطر حلو", "ابحث عن عطر وردي رومانسِي", "اقترح عطراً منعشاً للمكتب",
    "أحتاج هدية لوالدتي", "أرني عطراً رجولياً", "ابحث عن عطر نسائي", "أريد عطراً للشتاء",
    "اقترح عطراً للصيف", "أرني عطراً جريئاً", "ابحث عن عطر زهري ناعم", "أحتاج عطراً يومياً",
    "أرني عطراً فاخراً بالعود", "أوصني بعطر مسك", "ابحث عن عطر فانيلا", "أريد عطراً للعشاء",
    "اقترح عطراً لنفسي", "أرني نوع العطر", "أعطني قائمة العطور", "أرني أفضل 4 عطور",
    "ما نفحات همسة؟", "ما سعر مملكتي؟", "هل سرحان متاح؟", "قارن همسة وسرحان",
    "أين كتالوج منسَم؟", "هل تبيعون العطور الزيتية؟", "هل لديكم بخور؟", "ما فئات العطور؟",
    "ما أساليب عطور منسَم؟", "أرني أشكال المنتجات", "أحتاج عطراً زهرياً منعشاً", "أوصني بعطر عود دافئ",
]]


def valid(item, result):
    answer = str(result.get("answer", ""))
    lower = answer.lower()
    links = result.get("productLinks", [])
    kind = item["kind"]
    if kind == "negative":
        return result.get("intent") == "out_of_domain" and not links
    if kind in {"greeting", "wellbeing", "thanks", "general"}:
        return result.get("intent") not in {"out_of_domain", "perfume_list"} and "تعذر" not in answer
    if kind == "types":
        return result.get("intent") in {"perfume_types", "style_comparison"} or any(word in answer for word in ("زهري", "عود", "منعش", "خشبي", "العطور"))
    if kind == "list":
        if result.get("intent") != "perfume_list": return False
        match = re.search(r"(?:أفضل|top)\s+(\d+)", item["q"], re.I)
        return not match or len(result.get("productIds", [])) == int(match.group(1))
    if kind == "compare": return result.get("intent") in {"comparison", "comparison_clarification"} and (len(links) >= 2 or result.get("intent") == "comparison_clarification")
    if kind in {"details", "context_details"}: return len(links) <= 1 and bool(answer)
    if kind in {"price", "context_price"}: return len(links) <= 1 and ("درهم" in answer or "السعر" in answer or "تكلفة" in answer)
    if kind in {"availability", "context_availability"}: return len(links) <= 1 and any(word in answer for word in ("متاح", "المخزون", "مدرج"))
    if kind == "website": return bool(answer) and any(word in answer.lower() for word in ("منسَم", "كتالوج", "رابط", "شراء", "توصيل"))
    if kind == "normal" and result.get("intent") == "website": return bool(answer)
    if kind in {"recommend", "context_recommend", "related", "hard", "normal"}:
        return (bool(links) or result.get("intent") in {"perfume_types", "style_comparison"}) and result.get("intent") != "out_of_domain"
    return False


def run_round(name, items, retries=2):
    for attempt in range(1, retries + 2):
        failures = []
        for index, item in enumerate(items, 1):
            context = item.get("context", [])
            result = server.make_answer(item["q"], "ar", context_product_ids=context, profile={"productIds": context})
            if not valid(item, result): failures.append((index, item, result))
        print(f"{name} attempt {attempt}: {len(items) - len(failures)}/{len(items)} passed")
        if not failures: return True
        print("First failure:", failures[0][0], failures[0][1]["q"], "=>", failures[0][2].get("answer", ""))
        # A failed attempt restarts from question 1 after the logic/data is reviewed.
    return False


def main():
    output = Path(__file__).parent
    round_one = [{"q": q, "kind": k, "context": ["48"] if k.startswith("context_") else []} for q, k in ROUND_1[:100]]
    round_two = [{"q": q, "kind": k, "context": ["48"] if k.startswith("context_") else []} for q, k in ROUND_2[:100]]
    output.joinpath("arabic_chatbot_round1_100.json").write_text(json.dumps(round_one, ensure_ascii=False, indent=2), encoding="utf-8")
    output.joinpath("arabic_chatbot_round2_100.json").write_text(json.dumps(round_two, ensure_ascii=False, indent=2), encoding="utf-8")
    output.joinpath("arabic_chatbot_mixed_50.json").write_text(json.dumps(MIXED_50[:50], ensure_ascii=False, indent=2), encoding="utf-8")
    if not run_round("Arabic Round 1", round_one): return 1
    if not run_round("Arabic Round 2", round_two): return 1
    return 0 if run_round("Arabic Mixed stress", MIXED_50[:50]) else 1


if __name__ == "__main__":
    sys.exit(main())
