from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import random
import re
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen
import webbrowser

from intent_classifier import IntentClassifier


PROJECT_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_FILE = PROJECT_ROOT / "data" / "product-knowledge.json"
SSOT_FILE = PROJECT_ROOT / "data" / "ssot-knowledge.json"
LIVE_CATALOG_FILE = PROJECT_ROOT / "data" / "live-catalog.json"
GENERAL_INTENTS_FILE = PROJECT_ROOT / "data" / "general-chat-intents.json"
GENERAL_QA_FILE = PROJECT_ROOT / "general_qa_intents.json"
EXCEL_INTENTS_FILE = PROJECT_ROOT / "data" / "excel_intents.json"
MANSAM_SITE_URL = os.environ.get("MANSAM_SITE_URL", "https://uatuae.mansamworld.com").rstrip("/")
HF_API_URL = os.environ.get("HF_API_URL", "https://router.huggingface.co/v1/chat/completions")
HF_MODEL = os.environ.get("HF_MODEL", "Qwen/Qwen3.8-27B:deepinfra")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_TIMEOUT_SECONDS = min(max(int(os.environ.get("HF_TIMEOUT_SECONDS", "20")), 5), 60)
HF_GRADIO_SPACE = os.environ.get("HF_GRADIO_SPACE", "").rstrip("/")
HF_GRADIO_API_NAME = os.environ.get("HF_GRADIO_API_NAME", "/answer")
HF_GRADIO_TOKEN = os.environ.get("HF_GRADIO_TOKEN", HF_TOKEN)
ASR_MODEL = os.environ.get("ASR_MODEL", "openai/whisper-large-v3")
ASR_API_URL = os.environ.get("ASR_API_URL", f"https://router.huggingface.co/hf-inference/models/{ASR_MODEL}")
LIVE_REFRESH_SECONDS = max(int(os.environ.get("MANSAM_LIVE_REFRESH_SECONDS", "300")), 0)
LIVE_REFRESH_LOCK = threading.Lock()
LAST_LIVE_REFRESH = 0.0
LIVE_REFRESH_IN_PROGRESS = False
LIVE_SOURCE = {
    "name": {"en": "Live Mansam catalogue", "ar": "كتالوج منسَم المباشر"},
    "url": MANSAM_SITE_URL,
}
DOCUMENT_SOURCE = {
    "name": {"en": "Mansam product booklets", "ar": "كتيبات منتجات منسَم"},
}
STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "could", "for", "from", "i", "in", "is", "it", "its",
    "me", "my", "of", "or", "please", "the", "this", "that", "to", "want", "what", "which", "with", "you",
    "هل", "عن", "في", "من", "الى", "إلى", "على", "ما", "ماذا", "هذا", "هذه", "ذلك", "تلك", "اريد", "أريد",
    "لي", "لدي", "عندي", "هو", "هي", "مع", "او", "أو", "و", "كيف", "كم",
}
PREFERENCE_ALIASES = {
    "fresh": ("fresh", "citrus", "mint", "lemon", "bergamot", "clean", "daily", "everyday", "office", "work", "daytime", "light", "منعش", "منعشة", "خفيف", "خفيفة", "حمضيات", "نعناع", "ليمون", "يومي"),
    "floral": ("floral", "flowers", "jasmine", "lily", "tuberose", "زهري", "زهور", "ياسمين", "زنبق"),
    "rose": ("rose", "ورد", "وردي"),
    "oud": ("oud", "agarwood", "عود"),
    "woody": ("woody", "woods", "wood", "sandalwood", "خشبي", "أخشاب", "خشب"),
    "sweet": ("sweet", "vanilla", "fruity", "coffee", "musk", "حلو", "فانيليا", "فاكهي", "قهوة"),
    "warm": ("warm", "amber", "spicy", "saffron", "incense", "smoky", "smoke", "evening", "leather", "special occasion", "signature", "دافئ", "عنبر", "توابل", "زعفران", "بخور", "دخان", "دخانية"),
    "masculine": ("male", "men", "masculine", "him", "he", "husband", "boyfriend", "father", "son", "boy", "my boy", "man", "uncle", "brother", "رجال", "رجل", "لرجل", "رجالي", "للرجال", "له", "زوجي", "حبيبي", "والدي", "عمي", "أخي"),
    "feminine": ("female", "women", "woman", "lady", "girl", "wife", "girlfriend", "fiancee", "fiancée", "feminine", "her", "she", "mother", "daughter", "sister", "aunt", "grandmother", "نساء", "النساء", "نسائي", "للنساء", "لها", "زوجتي", "حبيبتي", "والدتي", "ابنتي", "سيدة", "امرأة", "خالتي", "عمتي", "أختي"),
    "summer": ("summer", "صيف", "صيفي"),
    "winter": ("winter", "شتاء", "شتوي"),
    "confident": ("confident", "bold", "strong", "powerful", "واثق", "جريء", "قوي", "قوية"),
    "romantic": ("romantic", "love", "passion", "رومانسي", "حب", "شغف"),
}
PERFUME_PRODUCT_LINES = {
    "eau de parfum 12ml", "eau de parfum 100ml", "natural oils and blends",
    "signature blends (attar)", "maamoul bukhoor", "luban", "dehab",
}
PERFUME_QUERY_TERMS = {"perfume", "perfumes", "fragrance", "fragrances", "scent", "scents", "عطر", "عطرا", "عطور"}
DOMAIN_QUERY_TERMS = PERFUME_QUERY_TERMS | {
    "attar", "attars", "oil", "oils", "candle", "candles", "bukhoor", "maamoul", "diffuser", "diffusers",
    "product", "products", "catalog", "catalogue", "collection", "notes", "ingredients", "price", "cost",
    "aed", "sar", "availability", "available", "stock", "website", "site", "shop", "store", "boutique",
    "link", "order", "shipping", "delivery", "boutique", "boutiques", "offer", "offers", "supply", "status", "mansam", "منسم", "عطار", "زيت", "زيوت", "شمعة", "شموع",
    "بخور", "معطر", "منتج", "منتجات", "كتالوج", "مجموعة", "نفحات", "مكونات", "السعر", "سعر", "متوفر",
    "متاحة", "رابط", "طلب", "شحن", "توصيل", "عروض", "خصم", "كوبون", "توريد", "ندرة", "متاجر", "متجر", "فئات", "نوع", "هدية", "هديه", "gift", "present", "ورد", "عود", "ياسمين", "مسك", "عنبر", "زهري", "زهرية", "منعش", "منعشة", "خشبي", "خشبية", "حلو", "حلوة", "فاكهي", "رومانسي", "جريء", "واثق", "دخان", "دخانية", "رائحه", "قوية", "ناعمة", "هادئة",
}
SOCIAL_QUERY_TERMS = {
    "hello", "hi", "hey", "hii", "good morning", "good afternoon", "good evening", "how are you", "i am fine",
    "im fine", "i'm fine", "i am good", "im good", "i'm good", "i am also fine", "i am doing well", "i feel great",
    "how is your day", "nice to meet you", "good day to you", "i am okay today", "i am feeling good", "i feel awesome", "that helped me", "what can you help me with", "you are helpful", "thanks", "thank you", "bye", "goodbye",
    "who are you", "what do you do", "what can you do", "my name is", "first time", "1st time", "this is my first time", "first time visit", "visited before", "for myself", "as a gift",
    "مرحباً", "مرحبا", "اهلا", "أهلاً", "صباح الخير", "مساء الخير", "كيف حالك", "أنا بخير", "أنا أيضاً بخير", "انا ايضا بخير", "أتمنى أن تكون بخير", "اتمنى ان تكون بخير", "أنا سعيد اليوم", "انا سعيد اليوم", "كيف تساعدني", "كيف تساعدني؟", "أنت مفيد", "انت مفيد", "ماذا يمكنك أن تفعل", "ماذا يمكنك ان تفعل", "من أنت", "من انت",
    "مرتي الأولى", "مرتي الاولى", "أول مرة", "اول مرة", "زرتكم من قبل", "لنفسي", "كهدية",
    "شكرا", "مع السلامة",
}


def localized(value, language="en"):
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("ar") or "")
    return str(value or "")


def string_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [item.strip() for item in str(value).split(",") if item.strip()]
    return []


def documentation_products(knowledge):
    products = []
    source_products = []
    seen_products = set()
    for product in knowledge.get("products", []):
        source_products.append(product)
    for product in knowledge.get("ssotProducts", []):
        source_products.append(product)
    for product in source_products:
        identity = product_key(product)
        if identity in seen_products:
            products = [item for item in products if product_key(item) != identity]
        seen_products.add(identity)
        if product.get("sourceType") == "ssot":
            products.append({**product})
            continue
        products.append({
            **product,
            "productLine": {"en": "Eau de Parfum", "ar": "ماء عطر"},
            "collection": {"en": product.get("collection", ""), "ar": product.get("collection", "")},
            "emotion": {"en": product.get("mood", ""), "ar": product.get("mood", "")},
            "volume": "100ml",
            "sourceType": "document",
        })
    for index, candle in enumerate(knowledge.get("candles", []), start=1):
        products.append({
            "id": f"document-candle-{index}",
            "name": candle["name"],
            "collection": {"en": "Handcrafted Candles", "ar": "شموع مصنوعة يدوياً"},
            "emotion": {"en": "Home fragrance", "ar": "عطر منزلي"},
            "productLine": {"en": "Scented Candles", "ar": "شموع معطرة"},
            "notes": candle["notes"],
            "description": {
                "en": "A Mansam handcrafted candle for a warm, fragrant home atmosphere.",
                "ar": "شمعة منسَم مصنوعة يدوياً لتمنح المنزل أجواءً دافئة وعطرة.",
            },
            "sourceType": "document",
        })
    return products


def product_key(product):
    value = normalize(localized(product.get("name"), "en"))
    value = re.sub(r"[^a-z0-9\u0600-\u06ff]+", "", value)
    return re.sub(r"(.)\1+", r"\1", value)


def load_catalog():
    with KNOWLEDGE_FILE.open(encoding="utf-8") as file:
        knowledge = json.load(file)
    if SSOT_FILE.exists():
        try:
            with SSOT_FILE.open(encoding="utf-8") as file:
                knowledge["ssotProducts"] = json.load(file).get("products", [])
        except (OSError, json.JSONDecodeError) as error:
            print(f"SSOT workbook data was not loaded: {type(error).__name__}")
    document_products = documentation_products(knowledge)
    product_by_key = {product_key(product): product for product in document_products}
    generated_at = ""

    if LIVE_CATALOG_FILE.exists():
        with LIVE_CATALOG_FILE.open(encoding="utf-8") as file:
            live_catalog = json.load(file)
        generated_at = live_catalog.get("generatedAt", "")
        live_products = live_catalog.get("products", [])
        for product in live_products:
            documented = product_by_key.get(product_key(product))
            if documented:
                product["documentation"] = documented
            product["sourceType"] = "live"
        return live_products + [
            product for key, product in product_by_key.items()
            if key not in {product_key(live_product) for live_product in live_products}
        ], generated_at

    return document_products, generated_at


def load_ssot_sheets():
    """Load every workbook sheet for grounded non-product questions."""
    if not SSOT_FILE.exists():
        return {}
    try:
        source = json.loads(SSOT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"SSOT sheet data was not loaded: {type(error).__name__}")
        return {}
    return {
        str(sheet): [row for row in rows if isinstance(row, dict) and any(str(value).strip() for value in row.values())]
        for sheet, rows in source.get("sheets", {}).items()
        if isinstance(rows, list)
    }


def is_arabic(text):
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))


def normalize(text):
    value = (text or "").lower()
    value = value.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    value = value.replace("ة", "ه").replace("ى", "ي")
    value = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", value)
    return value


def tokens(text):
    return {
        item for item in re.findall(r"[a-z0-9]+|[\u0600-\u06FF]+", normalize(text))
        if len(item) > 1 and item not in STOP_WORDS
    }


def load_general_qa_intents():
    """Adapt the supplied tag/pattern/response dataset to the local classifier format."""
    if not GENERAL_QA_FILE.exists():
        return []
    try:
        source = json.loads(GENERAL_QA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"General QA training data was not loaded: {type(error).__name__}")
        return []

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
            "responseOptions": {"en": responses},
        })
    return intents

def load_excel_intents():
    if not EXCEL_INTENTS_FILE.exists():
        return []
    try:
        source = json.loads(EXCEL_INTENTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Excel QA data was not loaded: {type(error).__name__}")
        return []

    intents = []
    for item in source.get("intents", []):
        tag = str(item.get("tag", "")).strip().lower()
        patterns = [str(value).strip() for value in item.get("patterns", []) if str(value).strip()]
        responses = [str(value).strip() for value in item.get("responses", []) if str(value).strip()]
        if not tag or not patterns or not responses:
            continue
        intents.append({
            "id": f"excel_{tag}",
            "examples": {"en": patterns},
            "response": {"en": responses[0], "ar": ""},
            "responseOptions": {"en": responses},
        })
    return intents


with GENERAL_INTENTS_FILE.open(encoding="utf-8") as file:
    GENERAL_INTENTS = json.load(file).get("intents", [])
GENERAL_QA_INTENTS = load_general_qa_intents() + load_excel_intents()
CONVERSATIONAL_INTENTS = GENERAL_QA_INTENTS + GENERAL_INTENTS
GENERAL_INTENT_BY_ID = {intent["id"]: intent for intent in CONVERSATIONAL_INTENTS}
GENERAL_INTENT_CLASSIFIER = IntentClassifier(GENERAL_INTENTS)
GENERAL_ENGLISH_INTENT_CLASSIFIER = IntentClassifier(CONVERSATIONAL_INTENTS)


CATALOG_PRODUCTS, CATALOG_UPDATED_AT = load_catalog()
SSOT_SHEETS = load_ssot_sheets()


def _refresh_live_catalog():
    global CATALOG_PRODUCTS, CATALOG_UPDATED_AT, LAST_LIVE_REFRESH, LIVE_REFRESH_IN_PROGRESS
    try:
        import sync_live_catalog
        sync_live_catalog.main()
        CATALOG_PRODUCTS, CATALOG_UPDATED_AT = load_catalog()
    except Exception as error:
        print(f"Live catalogue refresh skipped: {type(error).__name__}")
    finally:
        with LIVE_REFRESH_LOCK:
            LAST_LIVE_REFRESH = time.monotonic()
            LIVE_REFRESH_IN_PROGRESS = False


def refresh_live_catalog_if_needed():
    """Start a background public-catalogue refresh without delaying chat replies."""
    global LIVE_REFRESH_IN_PROGRESS
    if LIVE_REFRESH_SECONDS <= 0:
        return
    with LIVE_REFRESH_LOCK:
        if LIVE_REFRESH_IN_PROGRESS or time.monotonic() - LAST_LIVE_REFRESH < LIVE_REFRESH_SECONDS:
            return
        LIVE_REFRESH_IN_PROGRESS = True
    threading.Thread(target=_refresh_live_catalog, daemon=True).start()


def product_value(product, field, language="en"):
    return localized(product.get(field), language)


def product_notes(product, language="en"):
    return string_list(product.get("notes", {}).get(language, []))


def format_price(product):
    value = product.get("price")
    if value is None or value == "":
        return ""
    try:
        return f"{float(value):,.0f} {product.get('currency', 'AED')}"
    except (TypeError, ValueError):
        return f"{value} {product.get('currency', 'AED')}"


def catalog_text(product):
    documentation = product.get("documentation", {})
    values = [
        product_value(product, "name", "en"), product_value(product, "name", "ar"),
        product_value(product, "meaning", "en"), product_value(product, "description", "en"),
        product_value(product, "description", "ar"), product_value(product, "collection", "en"),
        product_value(product, "collection", "ar"), product_value(product, "emotion", "en"),
        product_value(product, "emotion", "ar"), product_value(product, "productLine", "en"),
        product_value(product, "productLine", "ar"), product.get("gender", ""), product.get("season", ""),
        product.get("volume", ""), product.get("packaging", ""), " ".join(product_notes(product, "en")),
        " ".join(product_notes(product, "ar")), product_value(documentation, "description", "en"),
        product_value(documentation, "description", "ar"), " ".join(product_notes(documentation, "en")),
        " ".join(product_notes(documentation, "ar")), product_value(product, "keywords", "en"),
        product_value(product, "keywords", "ar"), product_value(product, "idealFor", "en"),
        product_value(product, "idealFor", "ar"), product.get("sourceSheet", ""),
    ]
    return " ".join(str(value) for value in values if value)


def product_identity(product):
    return product_key(product) or normalize(product_value(product, "name", "ar")).replace(" ", "")


def query_term_matches(normalized_query, term):
    normalized_term = normalize(term)
    if re.fullmatch(r"[a-z0-9 ]+", normalized_term):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", normalized_query))
    if len(normalized_term) <= 2:
        return normalized_term in tokens(normalized_query)
    return normalized_term in normalized_query


def query_intent(query):
    normalized = normalize(query)
    return {
        "price": any(query_term_matches(normalized, word) for word in ("price", "cost", "aed", "how much", "السعر", "سعر", "كم سعر", "بكم", "تكلفة", "تكلفه")),
        "availability": any(query_term_matches(normalized, word) for word in ("available", "in stock", "stock", "availability", "متوفر", "المتوفر", "متاح", "متاحة", "مخزون")),
        "notes": any(query_term_matches(normalized, word) for word in ("notes", "ingredients", "smell", "نفحات", "مكونات", "رائحة")),
        "collection": any(query_term_matches(normalized, word) for word in ("collection", "line", "category", "مجموعة", "فئة")),
        "link": any(query_term_matches(normalized, word) for word in ("link", "url", "رابط")),
        "recommendation": any(query_term_matches(normalized, word) for word in ("recommend", "suggest", "best", "daily", "recommendation", "gift", "present", "اقترح", "انصح", "افضل", "يومي", "زهري", "زهرية", "الزهري", "الزهرية", "عود", "العود", "وردي", "الورد", "ورد", "مسك", "عنبر", "ياسمين", "عودي", "رجالي", "نسائي", "هدية", "هديه")),
        "follow_up": any(query_term_matches(normalized, word) for word in ("it", "this", "that", "its", "this perfume", "هذا", "هذه", "عنه", "له", "تفاصيله", "اريده", "اريدها", "لرجل", "لامرأة")),
    }


def is_domain_query(message, context_product_ids=None):
    """Keep factual answers inside Mansam's approved catalogue and website domain."""
    normalized = normalize(message)
    if context_product_ids or named_product_ids(message):
        return True
    # Mood and style phrases such as "bold and confident" are valid perfume
    # discovery queries even when they do not contain the word perfume.
    if query_preferences(message):
        return True
    if query_intent(message)["recommendation"]:
        return True
    if recipient_phrase(message, [], "en"):
        return True
    if any(query_term_matches(normalized, term) for term in DOMAIN_QUERY_TERMS):
        return True
    return any(query_term_matches(normalized, term) for term in SOCIAL_QUERY_TERMS)


def domain_refusal(language):
    if language == "ar":
        return "أستطيع مساعدتك فقط في عطور ومنتجات منسَم ومعلومات الموقع مثل النفحات والأسعار والتوفّر والروابط."
    return "I can help only with Mansam fragrances, products, and website information such as notes, prices, availability, and links."


def preference_alias_matches(alias, normalized_query, query_tokens):
    normalized_alias = normalize(alias)
    if " " in normalized_alias:
        return normalized_alias in normalized_query
    if normalized_alias in query_tokens:
        return True
    return len(normalized_alias) >= 4 and any(token.endswith(normalized_alias) for token in query_tokens)


def query_preferences(query):
    normalized = normalize(query)
    query_tokens = tokens(normalized)
    return [
        preference for preference, aliases in PREFERENCE_ALIASES.items()
        if any(preference_alias_matches(alias, normalized, query_tokens) for alias in aliases)
    ]


def conversation_preferences(conversation):
    """Keep useful customer preferences from the current browser chat only."""
    preferences = []
    for turn in conversation or []:
        if not isinstance(turn, dict) or turn.get("role") != "customer":
            continue
        for preference in query_preferences(str(turn.get("text", ""))):
            if preference not in preferences:
                preferences.append(preference)
    return preferences


def normalized_conversation(conversation):
    if not isinstance(conversation, list):
        return []
    turns = []
    for turn in conversation[-8:]:
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role", ""))
        text = str(turn.get("text", "")).strip()
        if role in ("customer", "assistant") and text:
            turns.append({"role": role, "text": text[:500]})
    return turns


def normalized_profile(profile):
    if not isinstance(profile, dict):
        return {"preferences": [], "productIds": []}
    allowed_preferences = set(PREFERENCE_ALIASES)
    preferences = [
        str(value) for value in profile.get("preferences", [])
        if str(value) in allowed_preferences
    ] if isinstance(profile.get("preferences"), list) else []
    product_ids = [str(value)[:80] for value in profile.get("productIds", [])[:3]] if isinstance(profile.get("productIds"), list) else []
    return {
        "preferences": list(dict.fromkeys(preferences)),
        "productIds": list(dict.fromkeys(product_ids)),
    }


def response_with_memory(response, preferences, product_ids):
    response["memory"] = {
        "preferences": list(dict.fromkeys(preferences))[:8],
        "productIds": list(dict.fromkeys(str(value) for value in product_ids))[:3],
    }
    return response


def named_product_ids(query):
    normalized = normalize(query)
    matches = []
    for product in CATALOG_PRODUCTS:
        names = (product_value(product, "name", "en"), product_value(product, "name", "ar"))
        if any(len(normalize(name)) > 3 and normalize(name) in normalized for name in names):
            matches.append(str(product.get("id")))
    return matches


def unique_products(products):
    unique = []
    seen = set()
    for product in products:
        identities = {
            product_key({"name": product.get("name", {}).get(language, "")})
            for language in ("en", "ar")
            if product.get("name", {}).get(language)
        }
        if seen.intersection(identities):
            continue
        seen.update(identities)
        unique.append(product)
    return unique


def is_comparison_request(message):
    normalized = normalize(message)
    return any(term in normalized for term in (
        "compare", "comparison", "difference between", "compare with", "which is better", "قارن", "مقارنة", "الفرق بين", "ايهما افضل", "أيهما أفضل"
    ))


def is_perfume_list_request(message):
    normalized = normalize(message)
    # Detail questions must stay attached to the current product. For example,
    # "show me the notes on this perfume" contains list-like words but is not a
    # request for a catalogue.
    detail_terms = (
        "notes", "ingredients", "smell", "scent", "price", "cost",
        "availability", "available", "stock", "collection", "line",
        "نفحات", "مكونات", "رائحة", "السعر", "متوفر", "مجموعة",
    )
    if any(query_term_matches(normalized, term) for term in detail_terms):
        return False
    if any(phrase in normalized for phrase in ("natural oils", "do you have oils", "do you have natural oils")):
        return True
    list_terms = ("list", "show me", "give me", "all", "catalog", "catalogue", "top", "قائمة", "قائمه", "اعرض", "ارني", "كل", "أفضل", "افضل")
    perfume_terms = PERFUME_QUERY_TERMS | {"attar", "oil", "oils", "bukhoor", "candle", "candles", "diffuser", "عطار", "بخور", "زيت", "شموع", "معطر"}
    list_request = any(term in normalized for term in list_terms)
    product_request = any(term in normalized for term in perfume_terms)
    product_request = product_request or any(term in normalized for term in ("women", "men", "attars", "bukhoor", "candles", "diffusers", "نساء", "النساء", "رجال", "الرجال"))
    list_request = list_request or "every" in normalized
    if "do you have" in normalized and any(term in normalized for term in ("attar", "bukhoor", "candle", "diffuser")):
        return True
    if any(phrase in normalized for phrase in ("هل لديكم", "هل لدي")) and any(term in normalized for term in ("عطر", "عطور", "منتج", "منتجات", "شموع", "بخور", "معطر", "زيت")):
        return True
    return list_request and product_request


def is_perfume_type_request(message):
    normalized = normalize(message)
    type_terms = ("type", "types", "kind", "kinds", "style", "styles", "category", "categories", "format", "formats", "نوع", "أنواع", "فئة", "فئات", "عائلات", "روائح", "اشكال")
    product_terms = PERFUME_QUERY_TERMS | {"product", "products", "catalog", "catalogue", "منتج", "منتجات", "كتالوج", "روائح", "عائلات", "اشكال"}
    return (any(query_term_matches(normalized, term) for term in type_terms) or "what products does mansam sell" in normalized) and any(query_term_matches(normalized, term) for term in product_terms)


def perfume_type_response(language):
    if language == "ar":
        return "أنواع العطور المتاحة في منسَم تشمل: منعشة وحمضية، زهرية، وردية، بالعود، خشبية، حلوة، دافئة ومتبلّة، ورومانسية. كما تتوفر بصيغ مثل ماء العطر والعطور الزيتية والبخور." 
    return "Mansam fragrance types include fresh and citrus-led, floral, rose, oud, woody, sweet, warm and spicy, and romantic styles. They are also available as Eau de Parfum, attars, and bukhoor."


def requested_product_lines(message):
    normalized = normalize(message)
    if any(term in normalized for term in ("attar", "oil", "oils", "عطار", "زيت", "زيوت")):
        return {"signature blends (attar)"}
    if any(term in normalized for term in ("candle", "candles", "شموع")):
        return {"scented candles"}
    if any(term in normalized for term in ("bukhoor", "maamoul", "بخور")):
        return {"maamoul bukhoor"}
    if any(term in normalized for term in ("diffuser", "diffusers", "معطر")):
        return {"home diffusers"}
    if any(term in normalized for term in PERFUME_QUERY_TERMS):
        return {"eau de parfum 100ml", "eau de parfum 12ml"}
    return set(PERFUME_PRODUCT_LINES)


def requested_list_label(message, language):
    normalized = normalize(message)
    labels = (
        (("attar", "oil", "oils", "عطار", "زيت", "زيوت"), "attars", "العطور الزيتية"),
        (("candle", "candles", "شموع"), "candles", "الشموع"),
        (("bukhoor", "maamoul", "بخور"), "bukhoor", "البخور"),
        (("diffuser", "diffusers", "معطر"), "diffusers", "معطرات المنزل"),
    )
    for terms, english, arabic in labels:
        if any(term in normalized for term in terms):
            return arabic if language == "ar" else english
    return "perfumes" if language == "en" else "العطور"


def requested_list_count(message):
    """Return the requested top-N size, or None when the customer wants the full list."""
    normalized = normalize(message)
    match = re.search(r"\btop\s+(\d{1,2})\b", normalized)
    if not match:
        match = re.search(r"(?:أفضل|افضل)\s+(\d{1,2})", normalized)
    if not match:
        return None
    return max(1, min(int(match.group(1)), 20))


def requested_recommendation_count(message, default=2):
    """Read a small quantity from a recommendation request such as "two perfumes"."""
    normalized = normalize(message)
    match = re.search(r"\b(\d{1,2})\s+(?:perfumes?|fragrances?|scents?|products?)\b", normalized)
    if not match:
        match = re.search(r"\b(\d{1,2})\s+(?:similar\s+)?(?:products?|perfumes?)\b", normalized)
    if not match:
        match = re.search(r"(?:suggest|recommend|show|give)\D{0,20}\b(\d{1,2})\b", normalized)
    if match:
        return max(1, min(int(match.group(1)), 20))
    number_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "واحد": 1, "اثنين": 2, "اثنان": 2, "ثلاثة": 3, "اربعة": 4, "أربعة": 4, "خمسة": 5}
    for word, count in number_words.items():
        if re.search(rf"(?:^|\s){re.escape(normalize(word))}(?:\s|$)", normalized):
            return count
    return default


def is_price_range_recommendation(message):
    normalized = normalize(message)
    return any(phrase in normalized for phrase in (
        "price range", "same price", "similar price", "within this price", "in this range",
        "نطاق السعر", "نفس السعر", "سعر مشابه", "ضمن هذا السعر", "في هذا النطاق",
    )) and any(query_term_matches(normalized, term) for term in ("suggest", "recommend", "show", "اقترح", "اعرض", "ارني"))


def is_similar_product_recommendation(message):
    normalized = normalize(message)
    return any(phrase in normalized for phrase in (
        "same category", "same type", "same kind", "similar product", "similar products", "similar to this product", "like this product",
        "like this", "like that", "similar to this", "similar to that",
        "similar perfume", "similar fragrance", "similar scent",
        "other products like this", "same collection", "نفس الفئة", "نفس النوع", "منتجات مشابهة",
        "نفس المجموعة",
    )) and any(query_term_matches(normalized, term) for term in ("suggest", "recommend", "show", "give", "اقترح", "اعرض", "ارني"))


def is_context_category_request(message):
    normalized = normalize(message)
    return any(phrase in normalized for phrase in (
        "this category", "that category", "this collection", "that collection",
        "هذه الفئة", "هذه المجموعة",
    )) and any(query_term_matches(normalized, term) for term in (
        "show", "give", "suggest", "recommend", "اعرض", "اقترح", "ارني",
    ))


def phrase_matches(message, example):
    normalized_message = normalize(message)
    normalized_example = normalize(example)
    if not normalized_example:
        return False
    if re.fullmatch(r"[a-z0-9 ]+", normalized_example):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalized_example)}(?![a-z0-9])", normalized_message))
    return normalized_example in normalized_message


FRIENDLY_INTENT_RESPONSES = {
    "greeting": {"en": ["Hello! How are you today?"], "ar": ["مرحباً! كيف حالك اليوم؟"]},
    "qa_greeting": {"en": ["Hello! How are you today?"]},
    "wellbeing": {"en": ["I'm doing well, thanks for asking. How are you?"], "ar": ["أنا بخير، شكراً لسؤالك. كيف حالك أنت؟"]},
    "qa_how_are_you": {"en": ["I'm doing well, thanks for asking. How are you?"]},
    "thanks": {"en": ["Anytime. Happy to help."], "ar": ["على الرحب والسعة، يسعدني مساعدتك."]},
    "qa_thanks": {"en": ["Anytime. Happy to help."]},
    "goodbye": {"en": ["Take care. Talk soon."], "ar": ["اعتن بنفسك، وأراك قريباً."]},
    "qa_goodbye": {"en": ["Take care. Talk soon."]},
    "identity": {"en": ["I'm Mansam's virtual fragrance companion. I can chat with you and help you explore the collection."], "ar": ["أنا المساعد الافتراضي لعطور منسَم. يمكننا الدردشة معاً واستكشاف المجموعة." ]},
    "qa_who_are_you": {"en": ["I'm Mansam's virtual fragrance companion. I can chat with you and help you explore the collection."]},
    "qa_apology": {"en": ["No worries at all. What would you like to talk about?"]},
    "qa_compliment_bot": {"en": ["That is kind of you. Thank you."]},
    "qa_insult_bot": {"en": ["I hear you. Let me try to be more helpful - what do you need?"]},
}


def intent_response(intent, message, language):
    friendly_options = FRIENDLY_INTENT_RESPONSES.get(intent.get("id"), {}).get(language, [])
    if friendly_options:
        return friendly_options[sum(ord(character) for character in normalize(message)) % len(friendly_options)]
    options = intent.get("responseOptions", {}).get(language, [])
    if not options:
        return localized(intent.get("response", {}), language)
    position = sum(ord(character) for character in normalize(message)) % len(options)
    return options[position]


def wellbeing_reply(message, language):
    """Catch friendly replies to the assistant before broad intent classification."""
    normalized = normalize(message).strip()
    english_replies = {
        "i am fine", "im fine", "i'm fine", "i am good", "im good", "i'm good",
        "i am fine how about you", "im fine how about you", "i'm fine how about you",
        "i am good how about you", "all good how about you", "fine how about you",
        "good how about you", "fine and you", "good and you",
    }
    positive_followups = {
        "i am also fine", "im also fine", "i'm also fine", "i am fine too", "im fine too", "i'm fine too",
        "i am also good", "im also good", "i'm also good", "i am good too", "im good too", "i'm good too",
        "doing well too", "i am doing well too", "im doing well too", "i'm doing well too",
    }
    arabic_replies = {"انا بخير", "بخير", "انا جيد", "انا تمام", "تمام وانت", "بخير وانت"}
    arabic_positive_followups = {"انا ايضا بخير", "أنا أيضاً بخير", "انا بخير ايضا", "أنا بخير أيضاً", "انا جيد ايضا", "انا تمام ايضا"}
    if language == "en" and normalized in positive_followups:
        return "Glad to hear that. What would you like to explore today?"
    if language == "en" and normalized in {"i am also fine", "i am doing well", "i feel great", "i feel happy", "how is your day"}:
        return "Glad to hear that. What would you like to explore today?"
    if language == "ar" and normalized in arabic_positive_followups:
        return "يسعدني سماع ذلك. ماذا تود أن نستكشف اليوم؟"
    if language == "en" and normalized in english_replies:
        return "I'm doing well too, thanks for asking. What's on your mind?"
    if language == "ar" and normalized in arabic_replies:
        return "أنا بخير أيضاً، شكراً لسؤالك. ما الذي تفكر فيه؟"
    return ""


def human_conversation_reply(message, language):
    """Handle broad, natural chat turns that do not need product retrieval."""
    normalized = normalize(message).strip()
    if language == "en":
        if normalized in {"nice to meet you", "good day to you", "how is your day", "how is your day going"}:
            return "Nice to meet you too. How can I help you discover a Mansam fragrance?", "conversation"
        if normalized in {"i am okay today", "i am feeling good", "i feel awesome", "that helped me", "what can you help me with"}:
            return "That is great to hear. I am here to help you explore Mansam fragrances.", "conversation"
        if normalized in {"what can you do", "what do you do"}:
            return "I can help you explore Mansam fragrances, compare products, and find notes, prices, and availability.", "identity"
        if normalized in {"you are helpful", "you are very helpful"}:
            return "That is kind of you. I am happy to help.", "qa_compliment_bot"
        if any(phrase in normalized for phrase in ("where can i find", "where can i view", "where can i see")) and any(word in normalized for word in ("catalog", "catalogue", "website", "site", "mansam")):
            return "You can explore the Mansam catalogue on the live website.", "website"
        if "catalogue" in normalized and "link" in normalized:
            return "You can explore the Mansam catalogue on the live website.", "website"
        if "how do i buy" in normalized and "mansam" in normalized:
            return "You can browse a product page from the Mansam catalogue and follow the purchase options there.", "website"
        if any(phrase in normalized for phrase in ("first time", "1st time", "never visited", "new customer", "new visitor", "first visit")):
            return "Welcome to Mansam Perfumes! Allow me to give you an idea of what we offer. Would you like a fragrance for yourself, or as a gift?", "first_time_greeting"
        if any(phrase in normalized for phrase in ("visited before", "visited your boutique", "bought before", "returning customer")):
            return "Welcome back to Mansam! Which fragrance did you enjoy previously, or what notes are you looking for today?", "returning_customer_greeting"
        if any(phrase in normalized for phrase in ("for myself", "just for me")):
            return "Wonderful. Do you lean more toward oud, rose, or musk? And which note do you not enjoy?", "for_myself_prompt"
        if any(phrase in normalized for phrase in ("as a gift", "for a gift", "gift for someone")):
            return "Lovely! Who is the gift for: a woman or a man? And do they prefer floral, woody, or warm oud scents?", "gift_prompt"
        if any(phrase in normalized for phrase in ("can you talk to me", "talk with me", "chat with me", "someone to chat", "keep me company", "lets chat", "let's chat")):
            return "Of course. I'm here with you - what's on your mind?", "conversation"
        if any(phrase in normalized for phrase in ("i have a question", "can i ask a question", "i want to ask", "may i ask", "i need to ask")):
            return "Of course. Ask away.", "question_invitation"
        if any(phrase in normalized for phrase in ("feel sad", "feeling sad", "little sad", "feel down", "bad day", "feel lonely", "feel tired", "not okay")):
            return "I'm sorry you're having a rough moment. I'm here to listen or help with whatever feels useful.", "support"
        if any(phrase in normalized for phrase in ("feel happy", "feeling good", "feel great", "feel awesome", "am excited")):
            return "That is lovely to hear. What's made your day better?", "positive_mood"
        if any(phrase in normalized for phrase in ("safe to use", "is this safe", "is this secure", "is my data safe", "private chat", "privacy")):
            return "Your privacy matters. For the exact data policy, please check the website's privacy policy.", "privacy"
        if any(phrase in normalized for phrase in ("what do you do for fun", "do you have hobbies", "what is your hobby")):
            return "I don't have hobbies like people do, but I do enjoy a good conversation. What do you enjoy?", "small_talk"
        if "meaning of life" in normalized:
            return "That is a big question. I think meaning often comes from the people, moments, and things we choose to care about.", "reflection"
    if language == "ar":
        if any(phrase in normalized for phrase in ("مرتي الأولى", "مرتي الاولى", "أول مرة", "اول مرة", "جديد", "أول زيارة")):
            return "أهلاً ومرحباً بك في منسَم! اسمح لي أن آخذك في جولة سريعة. هل تبحث عن العطر لنفسك أم كهدية؟", "first_time_greeting"
        if any(phrase in normalized for phrase in ("زرتكم من قبل", "زرت المتجر", "جربت منسم", "عميل سابق")):
            return "أهلاً بك مجدداً في منسَم! ما هو العطر الذي جربته وأعجبك سابقاً، أو ما هي النفحة التي تبحث عنها اليوم؟", "returning_customer_greeting"
        if any(phrase in normalized for phrase in ("لنفسي", "لي انا")):
            return "ممتاز! هل تميل أكثر إلى العود، الورد، أم المسك؟ وما هي النفحة التي لا تفضلها؟", "for_myself_prompt"
        if any(phrase in normalized for phrase in ("كهدية", "هدية لشخص", "اريد هدية")):
            return "فكرة جميلة! لمن ستكون الهدية: امرأة أم رجل؟ وهل يفضل النفحات الزهرية أم الخشبية أم العود الدافئ؟", "gift_prompt"
        if normalized in {"مرحباً", "مرحبا", "اهلا", "أهلاً", "صباح الخير", "مساء الخير"}:
            return "مرحباً! كيف حالك اليوم؟", "greeting"
        if normalized in {"ماذا يمكنك ان تفعل", "ماذا تستطيع ان تفعل", "من انت", "كيف تساعدني"}:
            return "يمكنني مساعدتك في اكتشاف عطور منسَم ومقارنة المنتجات ومعرفة النفحات والأسعار والتوفّر.", "identity"
        if normalized in {"انت مفيد", "انت مفيد جدا"}:
            return "هذا لطف منك. يسعدني مساعدتك.", "qa_compliment_bot"
        if normalized in {"اتمنى ان تكون بخير", "انا سعيد اليوم"}:
            return "شكراً لك. يسعدني أن أكون معك، ويمكنني مساعدتك في استكشاف عطور منسَم.", "conversation"
        if "كتالوج" in normalized or "منسم" in normalized:
            if any(phrase in normalized for phrase in ("اين", "رابط", "اشتري", "شراء", "اطلب", "توصيل", "كيف", "رؤية", "متجر")):
                return "يمكنك استكشاف كتالوج منسَم المباشر وفتح صفحة المنتج لمعرفة التفاصيل وخيارات الشراء.", "website"
        if any(phrase in normalized for phrase in ("تكلمني", "نتحدث", "دردشه", "دردشة", "اتحدث معك")):
            return "بالتأكيد، أنا هنا معك. ما الذي يشغل بالك؟", "conversation"
        if any(phrase in normalized for phrase in ("عندي سؤال", "اريد ان اسال", "أريد أن أسأل", "ممكن اسال", "ممكن أسأل")):
            return "بالتأكيد، اسأل ما تريد.", "question_invitation"
        if any(phrase in normalized for phrase in ("اشعر بالحزن", "اشعر اني حزين", "يوم سيء", "لست بخير", "متعب")):
            return "يؤسفني أنك تمر بوقت صعب. أنا هنا للاستماع أو للمساعدة بما يفيدك.", "support"
    return "", ""


def general_intent_response(message, language, context_product_ids=None):
    has_product_request = bool(query_preferences(message) or named_product_ids(message))
    has_product_request = has_product_request or bool(context_product_ids and query_intent(message)["follow_up"])
    intent_flags = query_intent(message)
    normalized_message = normalize(message).strip(" .?!")
    simple_recommendation = any(phrase in normalized_message for phrase in (
        "suggest me", "give me a suggestion", "what do you suggest", "recommend something"
    ))
    recipient_request = bool(recipient_phrase(message, [], language))
    product_terms = ("perfume", "fragrance", "scent", "attar", "attars", "oil", "oils", "candle", "product", "products", "عطر", "عطور", "رائحه", "منتج", "منتجات", "شموع")
    food_terms = ("food", "dish", "eat", "meal", "restaurant", "cuisine", "طعام", "طبق", "اكل", "أكل")
    is_food_request = any(term in normalize(message) for term in food_terms)
    if language == "ar" and any(phrase in normalized_message for phrase in ("كيف اطلب", "كيف اشتري", "اين اشتري")) and "منسم" in normalized_message:
        return {"language": language, "answer": "يمكنك تصفح كتالوج منسَم وفتح صفحة العطر الذي تريده ثم اتباع خيارات الشراء.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if language == "ar" and "توصيل" in normalized_message:
        return {"language": language, "answer": "يمكنك مراجعة خيارات التوصيل المتاحة من خلال كتالوج منسَم المباشر.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if normalized_message in {"tell me about mansam products", "what does mansam offer"}:
        return {"language": language, "answer": perfume_type_response(language), "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "perfume_types"}
    if language == "ar" and "المنتجات" in normalized_message and "منسم" in normalized_message:
        return {"language": language, "answer": perfume_type_response(language), "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "perfume_types"}
    if "can you show product links" in normalized_message:
        return {"language": language, "answer": "Yes. Tell me which Mansam perfume you would like a product link for.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if "live catalogue" in normalized_message or "live catalog" in normalized_message:
        return {"language": language, "answer": "The live Mansam catalogue contains perfumes, attars, bukhoor, candles, and home fragrance products.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if "where can i shop" in normalized_message:
        return {"language": language, "answer": "You can shop Mansam fragrances through the live Mansam catalogue website.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if "how do i buy" in normalized_message and "mansam" in normalized_message:
        return {"language": language, "answer": "You can browse a product page from the Mansam catalogue and follow the purchase options there.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    if "mansam order" in normalized_message or "how can i find a product page" in normalized_message:
        return {"language": language, "answer": "You can browse the Mansam catalogue and open the product page for the fragrance you want.", "sources": [LIVE_SOURCE], "productLinks": [], "productIds": [], "intent": "website"}
    is_catalog_question = any(intent_flags[key] for key in ("price", "availability", "notes", "collection", "follow_up"))
    is_catalog_question = is_catalog_question or ((intent_flags["recommendation"] or simple_recommendation or recipient_request) and not is_food_request)
    if has_product_request or is_catalog_question or any(term in normalize(message) for term in product_terms):
        return None

    reply = wellbeing_reply(message, language)
    if reply:
        return {
            "language": language,
            "answer": reply,
            "sources": [],
            "productLinks": [],
            "productIds": [],
            "intent": "wellbeing_reply",
        }

    answer, intent_id = human_conversation_reply(message, language)
    if answer:
        return {
            "language": language,
            "answer": answer,
            "sources": [],
            "productLinks": [],
            "productIds": [],
            "intent": intent_id,
        }

    matched_intent = None
    matched_length = 0
    for intent in CONVERSATIONAL_INTENTS:
        examples = intent.get("examples", {})
        phrases = examples.get("en", []) + examples.get("ar", [])
        for phrase in phrases:
            if phrase_matches(message, phrase) and len(normalize(phrase)) > matched_length:
                matched_intent = intent
                matched_length = len(normalize(phrase))
    if matched_intent:
        return {
            "language": language,
            "answer": intent_response(matched_intent, message, language),
            "sources": [],
            "productLinks": [],
            "productIds": [],
            "intent": matched_intent["id"],
        }

    # Let the trained classifier handle new conversational wording, but keep
    # fragrance, catalogue, and commercial questions on the grounded RAG path.
    classifier = GENERAL_ENGLISH_INTENT_CLASSIFIER if language == "en" else GENERAL_INTENT_CLASSIFIER
    predicted_intent, similarity = classifier.predict_with_similarity(message)
    if similarity < 0.44:
        answer = (
            "لم أفهم سؤالك تماماً، لكن يسعدني أن نتحدث عنه. هل يمكنك أن تخبرني المزيد؟"
            if language == "ar" else
            "I may not have understood that perfectly, but I'm happy to talk it through. Could you tell me a little more?"
        )
        return {"language": language, "answer": answer, "sources": [], "productLinks": [], "productIds": [], "intent": "general_fallback"}
    intent = GENERAL_INTENT_BY_ID.get(predicted_intent)
    if intent:
        return {
            "language": language,
            "answer": intent_response(intent, message, language),
            "sources": [],
            "productLinks": [],
            "productIds": [],
            "intent": intent["id"],
        }
    return None


def preference_label(preferences, language):
    labels = {
        "fresh": {"en": "fresh and citrus-led", "ar": "منعشة وحمضية"},
        "floral": {"en": "floral", "ar": "زهرية"},
        "rose": {"en": "rose", "ar": "وردية"},
        "oud": {"en": "oud", "ar": "بالعود"},
        "woody": {"en": "woody", "ar": "خشبية"},
        "sweet": {"en": "sweet", "ar": "حلوة"},
        "warm": {"en": "warm and spicy", "ar": "دافئة ومتبلّة"},
        "masculine": {"en": "masculine", "ar": "رجالية"},
        "feminine": {"en": "feminine", "ar": "نسائية"},
        "summer": {"en": "summer-friendly", "ar": "مناسبة للصيف"},
        "winter": {"en": "suited to winter", "ar": "مناسبة للشتاء"},
        "confident": {"en": "bold and confident", "ar": "جريئة وواثقة"},
        "romantic": {"en": "romantic", "ar": "رومانسية"},
    }
    return ", ".join(labels[item][language] for item in preferences[:3])


def recipient_phrase(message, preferences, language):
    """Keep a gift recipient's relationship in the recommendation wording."""
    normalized = normalize(message)
    relationship_labels = (
        (("girlfriend", "fiancee", "fiancée", "fiance", "حبيبتي"),
         {"en": "for your girlfriend", "ar": "لصديقتك"}),
        (("wife", "زوجتي"),
         {"en": "for your wife", "ar": "لزوجتك"}),
        (("boyfriend", "حبيبي"),
         {"en": "for your boyfriend", "ar": "لصديقك"}),
        (("boy", "my boy"),
         {"en": "for your boy", "ar": "لولدك"}),
        (("husband", "زوجي"),
         {"en": "for your husband", "ar": "لزوجك"}),
        (("daughter", "ابنتي"),
         {"en": "for your daughter", "ar": "لابنتك"}),
        (("son", "ابني"),
         {"en": "for your son", "ar": "لابنك"}),
        (("girl", "my girl", "woman", "my woman", "lady", "my lady"),
         {"en": "for a girl", "ar": "للفتاة"}),
        (("mother", "والدتي"),
         {"en": "for your mother", "ar": "لوالدتك"}),
        (("father", "والدي"),
         {"en": "for your father", "ar": "لوالدك"}),
        (("uncle", "عمي"),
         {"en": "for your uncle", "ar": "لعمك"}),
        (("aunt", "خالتي", "عمتي"),
         {"en": "for your aunt", "ar": "لخالتك"}),
        (("parent", "my parent", "grandmother", "grandma"),
         {"en": "for your parent", "ar": "لوالدك"}),
        (("brother", "أخي"),
         {"en": "for your brother", "ar": "لأخيك"}),
        (("sister", "أختي"),
         {"en": "for your sister", "ar": "لأختك"}),
        (("friend", "my friend", "صديقي", "صديقتي"),
         {"en": "for your friend", "ar": "لصديقك"}),
        (("cousin", "cusion", "my cousin", "my cusion"),
         {"en": "for your cousin", "ar": "لابن أو ابنة عمك"}),
        (("partner", "my partner", "colleague", "my colleague"),
         {"en": "for your partner", "ar": "لشريكك"}),
        (("myself", "for myself", "for me", "نفسي", "لي"),
         {"en": "for yourself", "ar": "لك"}),
        (("them", "for them", "themselves", "for themselves", "لهم", "لهم"),
         {"en": "for them", "ar": "لهم"}),
    )
    for aliases, labels in relationship_labels:
        if any(query_term_matches(normalized, alias) for alias in aliases):
            return labels[language]
    if "feminine" in preferences:
        return "for her" if language == "en" else "لها"
    if "masculine" in preferences:
        return "for him" if language == "en" else "له"
    return ""


def clarification(language, needs_product_name=False, message="", preferences=None):
    """Ask one useful next question instead of repeating a generic questionnaire."""
    normalized = normalize(message)
    preferences = set(preferences or [])
    is_gift = any(term in normalized for term in ("gift", "present", "هدية"))
    is_home = any(term in normalized for term in ("candle", "diffuser", "home", "room", "شموع", "شمعة", "معطر", "منزل", "غرفة"))

    if needs_product_name:
        answer = (
            "أكيد. ما اسم عطر منسَم الذي تريد معرفة تفاصيله أو سعره أو توفره؟"
            if language == "ar" else
            "Sure - which Mansam perfume would you like to check? I can look up its notes, price, or availability."
        )
    elif is_home:
        answer = (
            "فكرة جميلة. هل تحب أن تكون رائحة المنزل منعشة وخفيفة أم دافئة ومريحة؟"
            if language == "ar" else
            "Nice choice. Would you like your home fragrance to feel fresh and airy, or warm and cosy?"
        )
    elif is_gift:
        answer = (
            "فكرة جميلة. لمن ستكون الهدية: امرأة أم رجل؟"
            if language == "ar" else
            "Lovely. Who is the gift for: a woman or a man?"
        )
    elif "feminine" in preferences:
        answer = (
            "فهمت. هل تفضلين لها عطراً زهرياً ومنعشاً أم حلواً ودافئاً؟"
            if language == "ar" else
            "Got it. Would she prefer something floral and fresh, or sweet and warm?"
        )
    elif "masculine" in preferences:
        answer = (
            "تمام. هل يفضل عطراً منعشاً وحمضياً أم خشبياً ودافئاً أو بالعود؟"
            if language == "ar" else
            "Got it. Would he prefer fresh citrus, woody warmth, or an oud-led fragrance?"
        )
    elif preferences:
        answer = (
            "تمام. هل سيكون العطر للاستخدام اليومي أم للمساء أو لمناسبة خاصة؟"
            if language == "ar" else
            "Got it. Will you wear it daily, in the evening, or for a special occasion?"
        )
    else:
        answer = (
            "أكيد. لمن تبحث عن عطر: امرأة أم رجل أم كهدية؟"
            if language == "ar" else
            "Of course. Who are you choosing the fragrance for: a woman, a man, or a gift?"
        )
    return {"language": language, "answer": answer, "sources": [], "productLinks": [], "productIds": []}


def shorten_description(value, limit=430):
    value = " ".join((value or "").split())
    if len(value) <= limit:
        return value
    sentence_end = value.rfind(".", 0, limit)
    return value[:sentence_end + 1] if sentence_end > 120 else f"{value[:limit].rstrip()}..."


def ssot_record_text(sheet_name, record):
    return " ".join([sheet_name] + [f"{key} {value}" for key, value in record.items()])


def retrieve_ssot_records(query, limit=3):
    """Rank workbook rows by lexical overlap so answers stay inside the SSOT."""
    query_tokens = tokens(query)
    if not query_tokens:
        return []
    ranked = []
    for sheet_name, records in SSOT_SHEETS.items():
        for record in records:
            searchable = normalize(ssot_record_text(sheet_name, record))
            record_tokens = tokens(searchable)
            score = len(query_tokens & record_tokens)
            if normalize(sheet_name) in normalize(query):
                score += 4
            for key, value in record.items():
                if tokens(str(key)) & query_tokens:
                    score += 2
                if normalize(str(value)) in normalize(query) and str(value).strip():
                    score += 6
            if score:
                ranked.append((score, record, sheet_name))
    ranked.sort(key=lambda item: (-item[0], len(item[2])))
    return [(sheet, record) for _, record, sheet in ranked[:limit]]


def ssot_record_response(message, language):
    """Answer sheet-backed operational questions without exposing unrelated rows."""
    normalized_message = normalize(message)
    intent = query_intent(message)
    if any(query_term_matches(normalized_message, term) for term in SOCIAL_QUERY_TERMS):
        return None
    sheet_topics = {
        "boutique": "18_Boutiques", "boutiques": "18_Boutiques", "store": "18_Boutiques", "stores": "18_Boutiques",
        "offer": "19_Offers", "offers": "19_Offers", "coupon": "19_Offers", "discount": "19_Offers",
        "supply": "20_Supply_Status", "stock": "20_Supply_Status", "scarcity": "21_Scarcity_Phrases",
        "rare": "21_Scarcity_Phrases", "shipping": "22_Close_And_Shop", "delivery": "22_Close_And_Shop",
        "category": "24_Category_Purpose", "categories": "24_Category_Purpose", "type": "24_Category_Purpose",
        "بوتيك": "18_Boutiques", "متاجر": "18_Boutiques", "متجر": "18_Boutiques",
        "عروض": "19_Offers", "خصم": "19_Offers", "كوبون": "19_Offers",
        "توريد": "20_Supply_Status", "مخزون": "20_Supply_Status", "ندرة": "21_Scarcity_Phrases",
        "توصيل": "22_Close_And_Shop", "شحن": "22_Close_And_Shop", "فئات": "24_Category_Purpose", "نوع": "24_Category_Purpose",
    }
    requested_topics = {sheet for term, sheet in sheet_topics.items() if query_term_matches(normalized_message, term)}
    if any(phrase in normalized_message for phrase in ("what does mansam sell", "what does mansam offer", "what products do you have")):
        return None
    if query_preferences(message) or intent["recommendation"] or intent["price"] or intent["notes"] or (intent["collection"] and not requested_topics):
        return None
    if intent["availability"] and not requested_topics:
        return None
    if any(term in normalized_message for term in PERFUME_QUERY_TERMS) and not any(
        term in normalized_message for term in ("boutique", "store", "offer", "shipping", "delivery", "policy", "customer", "category", "type", "catalog", "catalogue")
    ):
        return None
    matches = retrieve_ssot_records(message, limit=1000 if requested_topics else 8)
    if requested_topics:
        prioritized = [(sheet, record) for sheet, record in matches if sheet in requested_topics]
        if prioritized:
            matches = prioritized[:8]
        else:
            matches = [
                (sheet, record)
                for sheet in requested_topics
                for record in SSOT_SHEETS.get(sheet, [])
            ][:8]
    if not matches or matches[0][0] in {"00_README", "01_Version_Log", "09_Conversation_Log_Schema"} and len(matches) == 1:
        return None
    visible = []
    for sheet_name, record in matches:
        fields = []
        for key, value in record.items():
            value = str(value).strip()
            if not value or key.lower() in {"id", "status", "sku", "product id"}:
                continue
            if language == "ar" and any(marker in key.lower() for marker in ("english", " en", "(en)")):
                continue
            if language == "en" and any(marker in key.lower() for marker in ("arabic", " ar", "(ar)")):
                continue
            fields.append(f"{key}: {value}")
        if fields:
            visible.append(f"{sheet_name}: " + "; ".join(fields[:5]))
    if not visible:
        return None
    if language == "ar":
        answer = "بحسب بيانات منسَم المعتمدة:\n" + "\n".join(visible)
    else:
        answer = "According to the approved Mansam workbook:\n" + "\n".join(visible)
    return {
        "language": language, "answer": answer, "sources": [DOCUMENT_SOURCE],
        "productLinks": [], "productIds": [], "intent": "ssot_sheet_answer",
    }


def retrieve_products(query, context_product_ids=None, limit=3, exclude_product_ids=None):
    query_normalized = normalize(query)
    query_tokens = tokens(query)
    preferences = query_preferences(query)
    named_ids = set(named_product_ids(query))
    category_terms = {"attar", "candle", "candles", "diffuser", "bukhoor", "luba", "oil", "oils", "perfume", "perfumes", "fragrance", "fragrances", "scent", "scents", "عطار", "شموع", "معطر", "بخور", "لبان", "زيت", "زيوت", "عطر", "عطور"}
    intent = query_intent(query)
    perfume_query = bool(query_tokens & PERFUME_QUERY_TERMS)
    has_context = bool(context_product_ids) and (
        intent["follow_up"] or intent["price"] or intent["availability"] or intent["notes"]
    )
    if not named_ids and not preferences and not has_context and not (query_tokens & category_terms):
        return []
    synonyms = {
        "fresh": ["citrus", "mint", "lemon", "bergamot", "neroli"],
        "daily": ["fresh", "citrus", "mint", "soft"],
        "rose": ["rose", "ورد"],
        "oud": ["oud", "عود"],
        "woody": ["woods", "wood", "sandalwood", "خشب", "اخشاب"],
        "floral": ["floral", "flowers", "rose", "jasmine", "زهور", "ورد", "ياسمين"],
        "men": ["male", "masculine"],
        "male": ["men", "masculine"],
        "women": ["female", "feminine"],
        "female": ["women", "feminine"],
        "summer": ["fresh", "citrus"],
        "winter": ["oud", "amber", "vanilla", "woods"],
        "candle": ["candles", "home", "fragrance"],
        "diffuser": ["home", "fragrance"],
        "attar": ["signature", "blends"],
        "منعش": ["fresh", "citrus", "mint", "lemon", "bergamot"],
        "منعشا": ["fresh", "citrus", "mint", "lemon", "bergamot"],
        "يومي": ["fresh", "citrus", "mint", "soft"],
        "اليومي": ["fresh", "citrus", "mint", "soft"],
        "وردي": ["rose", "ورد"],
        "خشبي": ["woods", "wood", "sandalwood", "خشب", "اخشاب"],
        "زهري": ["floral", "flowers", "rose", "jasmine", "زهور", "ورد", "ياسمين"],
        "رجالي": ["male", "men", "masculine"],
        "نسائي": ["female", "women", "feminine"],
        "صيفي": ["summer", "fresh", "citrus"],
        "شتوي": ["winter", "oud", "amber", "vanilla"],
        "شموع": ["candle", "candles", "home"],
        "عطار": ["attar", "signature", "blends"],
        "معطر": ["diffuser", "home", "fragrance"]
    }
    expanded_tokens = set(query_tokens)
    for preference in preferences:
        for alias in PREFERENCE_ALIASES[preference]:
            expanded_tokens.update(tokens(alias))
    for item in query_tokens:
        expanded_tokens.update(synonyms.get(item, []))

    context_primary_id = str((context_product_ids or [""])[0])
    context_product_ids = {str(product_id) for product_id in (context_product_ids or [])}
    ranked = []
    for product in CATALOG_PRODUCTS:
        document = normalize(catalog_text(product))
        document_tokens = tokens(document)
        notes = tokens(" ".join(product_notes(product, "en") + product_notes(product, "ar")))
        descriptions = tokens(product_value(product, "description", "en") + " " + product_value(product, "description", "ar"))
        score = len(expanded_tokens & document_tokens)
        score += 3 * len(expanded_tokens & notes)
        score += len(expanded_tokens & descriptions)
        score += 5 * len(expanded_tokens & tokens(
            product_value(product, "productLine", "en") + " " + product_value(product, "productLine", "ar")
        ))
        if perfume_query:
            product_line = normalize(product_value(product, "productLine", "en")).strip()
            score += 12 if product_line in PERFUME_PRODUCT_LINES else -8
        if normalize(product_value(product, "name", "en")) in query_normalized:
            score += 12
        if normalize(product_value(product, "name", "ar")) in query_normalized:
            score += 12
        if str(product.get("id")) in named_ids:
            score += 30
        if has_context:
            if context_primary_id and str(product.get("id")) == context_primary_id:
                score += 40
            elif str(product.get("id")) in context_product_ids:
                score += 5
        if "12" not in query_tokens and product.get("volume") == "100ml":
            score += 1
        if product.get("sourceType") == "live":
            score += 1
        if score:
            ranked.append((score, product))

    excluded = {str(product_id) for product_id in (exclude_product_ids or [])}
    excluded_identities = {
        product_identity(product)
        for product in CATALOG_PRODUCTS
        if str(product.get("id")) in excluded
    }
    ranked.sort(key=lambda item: (-item[0], random.SystemRandom().random()))
    unique_products = []
    seen_names = set()
    for _, product in ranked:
        if str(product.get("id")) in excluded or product_identity(product) in excluded_identities:
            continue
        identity = product_identity(product)
        if identity in seen_names:
            continue
        seen_names.add(identity)
        unique_products.append(product)
        if len(unique_products) == limit:
            break
    return unique_products


def status_text(product, language):
    if product.get("sourceType") != "live":
        return ""
    available = product.get("available")
    if language == "ar":
        return "والمنتج مدرج كمتوفر حالياً في الكتالوج المباشر." if available else "والمنتج غير مدرج كمتوفر حالياً في الكتالوج المباشر."
    return "It is currently listed as available in the live catalogue." if available else "It is not currently listed as available in the live catalogue."


def product_source(product):
    sources = [LIVE_SOURCE] if product.get("sourceType") == "live" else []
    if product.get("documentation") or product.get("sourceType") == "document":
        sources.append(DOCUMENT_SOURCE)
    return sources or [DOCUMENT_SOURCE]


def product_url(product):
    if product.get("sourceUrl"):
        return str(product["sourceUrl"])
    product_id = product.get("productId") or product.get("id")
    product_line = product_value(product, "productLine", "en")
    product_name = product_value(product, "name", "en")
    if not product_id or not product_line or not product_name:
        return ""

    def route_part(value):
        return quote(re.sub(r"[()]", "", re.sub(r"\s+", "_", value.strip())))

    return f"{MANSAM_SITE_URL}/productDetails/{route_part(product_line)}/{route_part(product_name)}/{product_id}"


def hugging_face_product_context(products, language):
    context = []
    for product in products[:3]:
        item = {
            "name": product_value(product, "name", language),
            "productLine": product_value(product, "productLine", language),
            "collection": product_value(product, "collection", language),
            "description": product_value(product, "description", language),
            "notes": product_notes(product, language),
            "gender": product.get("gender", ""),
            "season": product.get("season", ""),
            "keywords": product_value(product, "keywords", language),
            "idealFor": product_value(product, "idealFor", language),
        }
        if product.get("price") is not None:
            try:
                item["price"] = f"{float(product['price']):,.0f} {product.get('currency', 'AED')}"
            except (TypeError, ValueError):
                item["price"] = str(product["price"])
        if product.get("sourceType") == "live":
            item["available"] = bool(product.get("available"))
        context.append(item)
    return context


def hugging_face_answer(message, language, products):
    """Use an optional hosted model only to phrase RAG-retrieved product facts."""
    if HF_GRADIO_SPACE:
        return hugging_face_gradio_answer(message, language, products)
    if not HF_TOKEN:
        return ""

    language_name = "Arabic" if language == "ar" else "English"
    system_message = (
        "You are a warm Mansam fragrance companion. Reply in " + language_name + ". "
        "Use only the supplied Mansam catalogue context. Do not invent facts, prices, "
        "availability, policies, shipping details, or product names. Sound natural and "
        "thoughtful, like a helpful boutique friend, without claiming to be human. Give a "
        "concise answer in at most 120 words. Do not answer questions outside Mansam's "
        "fragrance catalogue and website domain. Do not add URLs because the website "
        "renders verified product links separately."
    )
    user_message = "Customer question:\n" + message + "\n\nVerified Mansam catalogue context:\n" + json.dumps(
        hugging_face_product_context(products, language), ensure_ascii=False
    )
    payload = {
        "model": HF_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
        "max_tokens": 260,
    }
    request = Request(
        HF_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=HF_TIMEOUT_SECONDS) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        print(f"Hugging Face chat fallback: {type(error).__name__}")
        return ""
    except json.JSONDecodeError:
        print("Hugging Face chat fallback: invalid JSON response")
        return ""

    choices = result.get("choices", [])
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    if isinstance(content, list):
        content = " ".join(item.get("text", "") for item in content if isinstance(item, dict))
    return str(content).strip()[:1200]


def hugging_face_gradio_answer(message, language, products):
    """Use a Gradio Space through its authenticated Hugging Face client API."""
    if not HF_GRADIO_TOKEN:
        return ""

    try:
        from gradio_client import Client
    except ImportError:
        print("Hugging Face Gradio fallback: install gradio_client")
        return ""

    language_name = "Arabic" if language == "ar" else "English"
    prompt = (
        "You are a warm Mansam fragrance companion. Reply only in " + language_name + ". "
        "Use only the verified catalogue context below. Do not invent products, prices, "
        "availability, policies, or links. Sound natural and thoughtful, like a helpful "
        "boutique friend, without claiming to be human. Answer only Mansam fragrance or "
        "website questions. Keep the reply below 120 words.\n\n"
        "Customer question:\n" + message + "\n\nVerified Mansam catalogue context:\n" + json.dumps(
            hugging_face_product_context(products, language), ensure_ascii=False
        )
    )
    try:
        client = Client(
            HF_GRADIO_SPACE,
            oauth_token=HF_GRADIO_TOKEN,
            verbose=False,
            httpx_kwargs={"timeout": HF_TIMEOUT_SECONDS},
        )
        result = client.predict(in_0=prompt, api_name=HF_GRADIO_API_NAME)
    except Exception as error:
        print(f"Hugging Face Gradio fallback: {type(error).__name__}")
        return ""

    answer = str(result).strip()
    if not answer or "Please sign in with Hugging Face" in answer:
        print("Hugging Face Gradio fallback: authentication was not accepted")
        return ""
    return answer[:1200]


def make_answer(message, language, context_product_ids=None, conversation=None, profile=None):
    language = "ar" if language == "ar" or is_arabic(message) else "en"
    conversation = normalized_conversation(conversation)
    profile = normalized_profile(profile)
    context_product_ids = list(dict.fromkeys(profile["productIds"] + [str(value) for value in (context_product_ids or [])]))[:3]
    if not is_domain_query(message, context_product_ids):
        return response_with_memory({
            "language": language, "answer": domain_refusal(language), "sources": [],
            "productLinks": [], "productIds": [], "intent": "out_of_domain",
        }, profile["preferences"], context_product_ids)
    preferences = profile["preferences"] + [
        preference for preference in conversation_preferences(conversation)
        if preference not in profile["preferences"]
    ]
    current_preferences = query_preferences(message)
    # A new gender request supersedes an earlier recipient from this chat.
    if "masculine" in current_preferences and "feminine" not in current_preferences:
        preferences = [preference for preference in preferences if preference != "feminine"]
    elif "feminine" in current_preferences and "masculine" not in current_preferences:
        preferences = [preference for preference in preferences if preference != "masculine"]
    for preference in current_preferences:
        if preference not in preferences:
            preferences.append(preference)

    intent = query_intent(message)
    has_context = bool(context_product_ids) and (
        intent["follow_up"] or intent["price"] or intent["availability"] or intent["notes"]
    )
    direct_product_ids = named_product_ids(message)

    if is_context_category_request(message):
        reference = next((product for product_id in context_product_ids
                          for product in CATALOG_PRODUCTS if str(product.get("id")) == product_id), None)
        if reference is None:
            return response_with_memory({
                "language": language,
                "answer": "Which category or perfume do you mean?" if language == "en" else "أي فئة أو عطر تقصد؟",
                "sources": [], "productLinks": [], "productIds": [], "intent": "category_clarification",
            }, preferences, [])
        field = "collection" if any(term in normalize(message) for term in ("collection", "المجموعة")) else "productLine"
        category = product_value(reference, field, "en")
        if not category:
            return response_with_memory({
                "language": language,
                "answer": "Which category would you like to explore?" if language == "en" else "أي فئة ترغب في استكشافها؟",
                "sources": [], "productLinks": [], "productIds": [], "intent": "category_clarification",
            }, preferences, context_product_ids)
        count = requested_recommendation_count(message)
        candidates = unique_products([product for product in CATALOG_PRODUCTS
                                      if product_value(product, field, "en") == category])
        candidates.sort(key=lambda product: str(product.get("id")) in context_product_ids)
        matches = candidates[:count]
        label = product_value(reference, field, language)
        heading = (f"Here are {len(matches)} products in {label}:" if language == "en"
                   else f"إليك {len(matches)} منتجات من {label}:")
        if len(matches) < count:
            heading = (f"I found only {len(matches)} products in {label}:" if language == "en"
                       else f"وجدت {len(matches)} منتجات فقط من {label}:")
        lines = [f"{index}. {product_value(product, 'name', language).strip()}"
                 + (f" — {format_price(product)}" if format_price(product) else "")
                 for index, product in enumerate(matches, 1)]
        return response_with_memory({
            "language": language, "answer": heading + "\n\n" + "\n".join(lines),
            "sources": product_source(reference), "intent": "category_recommendation",
            "productIds": [str(product.get("id")) for product in matches],
            "productLinks": [{"name": product.get("name", {}), "url": product_url(product)}
                             for product in matches if product_url(product)],
        }, preferences, [str(product.get("id")) for product in matches])

    if intent["link"] and direct_product_ids:
        product = next((item for item in CATALOG_PRODUCTS if str(item.get("id")) == direct_product_ids[0]), None)
        if product:
            answer = (
                f"إليك رابط منتج منسَم لعطر {product_value(product, 'name', language)}."
                if language == "ar" else
                f"Here is the Mansam product link for {product_value(product, 'name', language)}."
            )
            return response_with_memory({
                "language": language, "answer": answer, "sources": product_source(product),
                "productLinks": [{"name": product.get("name", {}), "url": product_url(product)}] if product_url(product) else [],
                "productIds": [str(product.get("id"))], "intent": "product_link",
            }, preferences, [str(product.get("id"))])

    if context_product_ids and (is_price_range_recommendation(message) or is_similar_product_recommendation(message)):
        by_id = {str(product.get("id")): product for product in CATALOG_PRODUCTS}
        reference = next((by_id[product_id] for product_id in context_product_ids if product_id in by_id), None)
        requested_count = requested_recommendation_count(message)
        try:
            reference_price = float(reference.get("price")) if reference else None
        except (TypeError, ValueError):
            reference_price = None
        candidates = [product for product in CATALOG_PRODUCTS if str(product.get("id")) not in context_product_ids]
        if is_similar_product_recommendation(message) and reference:
            reference_line = product_value(reference, "productLine", "en")
            reference_collection = product_value(reference, "collection", "en")
            same_category = [
                product for product in candidates
                if (reference_line and product_value(product, "productLine", "en") == reference_line)
                or (reference_collection and product_value(product, "collection", "en") == reference_collection)
            ]
            if len(unique_products(same_category)) >= requested_count:
                candidates = same_category
            else:
                # A small collection must not silently reduce the requested count.
                candidates = [product for product in candidates if product in same_category or
                              normalize(product_value(product, "productLine", "en")) in PERFUME_PRODUCT_LINES]
        if reference_price is not None and is_price_range_recommendation(message):
            close_matches = []
            for product in candidates:
                try:
                    price = float(product.get("price"))
                except (TypeError, ValueError):
                    continue
                if abs(price - reference_price) <= max(reference_price * 0.2, 20):
                    close_matches.append((abs(price - reference_price), product))
            close_matches.sort(key=lambda item: item[0])
            matches = [product for _, product in close_matches]
            if len(matches) < requested_count:
                remaining = []
                for product in candidates:
                    try:
                        remaining.append((abs(float(product.get("price")) - reference_price), product))
                    except (TypeError, ValueError):
                        continue
                matches += [product for _, product in sorted(remaining) if product not in matches]
        elif is_similar_product_recommendation(message):
            # Rank by scent overlap instead of the order of the live catalogue.
            reference_notes = set(tokens(" ".join(product_notes(reference, "en")))) if reference else set()
            preferred_notes = set(tokens(" ".join(
                turn["text"] for turn in conversation if turn["role"] == "customer"
            )))

            def similarity_score(product):
                notes = set(tokens(" ".join(product_notes(product, "en"))))
                shared = notes & reference_notes
                union = notes | reference_notes
                return (
                    len(notes & preferred_notes),
                    len(shared) / len(union) if union else 0,
                    bool(reference and product_value(product, "collection", "en") == product_value(reference, "collection", "en")),
                )

            matches = sorted(unique_products(candidates), key=similarity_score, reverse=True)[:requested_count]
        else:
            matches = []
        matches = matches[:requested_count]
        if matches:
                names = ", ".join(f"{product_value(product, 'name', language)} ({format_price(product)})" for product in matches)
                is_price_match = is_price_range_recommendation(message)
                answer = (
                    f"Here are {len(matches)} other Mansam perfumes in a similar price range to {product_value(reference, 'name', language)}: {names}."
                    if is_price_match else
                    f"Here are {len(matches)} alternatives to {product_value(reference, 'name', language)}, selected using fragrance notes and your preferences: {names}."
                    if language == "en" else
                    f"إليك {len(matches)} بدائل لعطر {product_value(reference, 'name', language)}، بناءً على النفحات العطرية وتفضيلاتك: {names}."
                )
                if language == "ar" and is_price_match:
                    answer = f"إليك {len(matches)} عطور أخرى من منسَم ضمن نطاق سعري مشابه لسعر {product_value(reference, 'name', language)}: {names}."
                return response_with_memory({
                    "language": language, "answer": answer, "sources": [LIVE_SOURCE],
                    "productLinks": [{"name": product.get("name", {}), "url": product_url(product)} for product in matches if product_url(product)],
                    "productIds": [str(product.get("id")) for product in matches], "intent": "price_range_recommendation" if is_price_range_recommendation(message) else "similar_product_recommendation",
                }, preferences, [str(product.get("id")) for product in matches])

    if is_comparison_request(message) and not direct_product_ids and any(
        query_term_matches(normalize(message), term) for term in ("oud", "floral", "fresh", "woody", "sweet", "warm", "عود", "زهري", "زهرية", "منعش", "منعشة", "خشبي", "حلو", "دافئ")
    ):
        answer = (
            "Oud fragrances are deep, woody, smoky, and warm, while floral fragrances are centered on flowers such as rose, jasmine, and lily."
            if language == "en" else
            "العطور بالعود عميقة وخشبية ودافئة، بينما تركز العطور الزهرية على روائح مثل الورد والياسمين والزنبق."
        )
        return response_with_memory({
            "language": language, "answer": answer, "sources": [LIVE_SOURCE],
            "productLinks": [], "productIds": [], "intent": "style_comparison",
        }, preferences, context_product_ids)

    if is_comparison_request(message):
        comparison_ids = list(dict.fromkeys(named_product_ids(message) + context_product_ids))
        comparison_products = unique_products([
            product for product in CATALOG_PRODUCTS
            if str(product.get("id")) in comparison_ids
        ])[:2]
        if len(comparison_products) < 2:
            answer = (
                "يرجى ذكر اسمي العطرين اللذين تريد مقارنتهما، مثل: قارن بين عطر A وعطر B."
                if language == "ar" else
                "Which two perfume names would you like me to compare? For example: compare Perfume A with Perfume B."
            )
            return response_with_memory({
                "language": language, "answer": answer, "sources": [],
                "productLinks": [], "productIds": [], "intent": "comparison_clarification",
            }, preferences, context_product_ids)

        def comparison_details(product, detail_language):
            perfume_name = product_value(product, "name", detail_language)
            perfume_notes = ", ".join(product_notes(product, detail_language)[:5])
            perfume_collection = product_value(product, "collection", detail_language)
            perfume_price = product.get("price")
            price_text = f" {format_price(product)}" if perfume_price is not None else ""
            return perfume_name, perfume_notes, perfume_collection, price_text

        first, second = [comparison_details(product, language) for product in comparison_products]
        if language == "ar":
            answer = (
                f"مقارنة سريعة:\n{first[0]}: {first[1] or 'النفحات غير مذكورة'}"
                f"{('، من مجموعة ' + first[2]) if first[2] else ''}{('، السعر ' + first[3].strip()) if first[3] else ''}.\n"
                f"{second[0]}: {second[1] or 'النفحات غير مذكورة'}"
                f"{('، من مجموعة ' + second[2]) if second[2] else ''}{('، السعر ' + second[3].strip()) if second[3] else ''}."
            )
        else:
            answer = (
                f"Here is a quick comparison:\n{first[0]}: {first[1] or 'notes not listed'}"
                f"{(' from the ' + first[2] + ' collection') if first[2] else ''}{(' - ' + first[3].strip()) if first[3] else ''}.\n"
                f"{second[0]}: {second[1] or 'notes not listed'}"
                f"{(' from the ' + second[2] + ' collection') if second[2] else ''}{(' - ' + second[3].strip()) if second[3] else ''}."
            )
        return response_with_memory({
            "language": language, "answer": answer, "sources": [LIVE_SOURCE],
            "productLinks": [
                {"name": product.get("name", {}), "url": product_url(product)}
                for product in comparison_products if product_url(product)
            ],
            "productIds": [str(product.get("id")) for product in comparison_products],
            "intent": "comparison",
        }, preferences, [str(product.get("id")) for product in comparison_products])

    if is_perfume_type_request(message) and not has_context:
        return response_with_memory({
            "language": language, "answer": perfume_type_response(language), "sources": [LIVE_SOURCE],
            "productLinks": [], "productIds": [], "intent": "perfume_types",
        }, preferences, context_product_ids)

    # A product follow-up such as "show me the notes on this perfume" must be
    # answered from the remembered product, never expanded into a full list.
    if is_perfume_list_request(message) and not has_context:
        requested_count = requested_list_count(message)
        list_query = f"{message} perfume"
        product_lines = requested_product_lines(message)
        listed_products = unique_products([
            product for product in retrieve_products(list_query, limit=100)
            if normalize(product_value(product, "productLine", "en")).strip() in product_lines
        ])
        if not listed_products:
            listed_products = unique_products([
                product for product in CATALOG_PRODUCTS
                if normalize(product_value(product, "productLine", "en")).strip() in product_lines
            ])
        if requested_count:
            listed_products = listed_products[:requested_count]
        names = ", ".join(product_value(product, "name", language) for product in listed_products)
        list_label = preference_label(preferences, language)
        label = requested_list_label(message, language)
        if language == "ar":
            answer = f"وجدت {len(listed_products)} {label}{(' لفئة ' + list_label) if list_label else ''}: {names}."
        else:
            answer = f"I found {len(listed_products)} {label}{(' for the ' + list_label + ' style') if list_label else ''}: {names}."
        return response_with_memory({
            "language": language, "answer": answer, "sources": [LIVE_SOURCE],
            "productLinks": [
                {"name": product.get("name", {}), "url": product_url(product)}
                for product in listed_products if product_url(product)
            ],
            "productIds": [str(product.get("id")) for product in listed_products],
            "intent": "perfume_list",
        }, preferences, [str(product.get("id")) for product in listed_products])

    sheet_response = ssot_record_response(message, language)
    if sheet_response:
        return response_with_memory(sheet_response, preferences, context_product_ids)
    general_response = general_intent_response(message, language, context_product_ids)
    if general_response:
        return response_with_memory(general_response, preferences, context_product_ids)
    normalized_message = normalize(message)
    simple_recommendation = any(phrase in normalized_message for phrase in (
        "suggest me", "give me a suggestion", "what do you suggest", "recommend something"
    ))
    is_food_request = any(term in normalized_message for term in (
        "food", "dish", "eat", "meal", "restaurant", "cuisine", "طعام", "طبق", "اكل", "أكل"
    ))
    recipient_request = bool(recipient_phrase(message, preferences, language))
    generic_recommendation = (intent["recommendation"] or simple_recommendation or recipient_request or (
        any(query_term_matches(normalized_message, term) for term in PERFUME_QUERY_TERMS)
        and not any(intent[key] for key in ("price", "availability", "notes", "collection", "follow_up"))
    )) and not is_food_request and not direct_product_ids and not has_context
    if (intent["price"] or intent["availability"] or intent["notes"]) and not intent["recommendation"] and not direct_product_ids and not has_context and not preferences:
        return response_with_memory(
            clarification(language, needs_product_name=True, message=message, preferences=preferences),
            preferences,
            context_product_ids,
        )
    retrieval_message = " ".join([message, "perfume"] + preferences) if generic_recommendation else " ".join([message] + preferences)
    recommendation_mode = (bool(preferences) or generic_recommendation) and not direct_product_ids and not has_context
    detail_follow_up = has_context and any(
        intent[key] for key in ("notes", "price", "availability", "collection")
    )
    if detail_follow_up:
        # Preserve the conversation's product order. Semantic retrieval can
        # otherwise replace "this perfume" with a different close match.
        by_id = {str(product.get("id")): product for product in CATALOG_PRODUCTS}
        matches = [by_id[product_id] for product_id in context_product_ids if product_id in by_id]
        matches = matches[:3]
    else:
        matches = retrieve_products(
            retrieval_message,
            context_product_ids,
            limit=25 if recommendation_mode else 3,
            exclude_product_ids=context_product_ids if recommendation_mode else [],
        )
    if not matches and recommendation_mode:
        matches = retrieve_products(retrieval_message, context_product_ids)
    if recommendation_mode and matches:
        random.SystemRandom().shuffle(matches)

    if not matches:
        return response_with_memory(
            clarification(language, message=message, preferences=preferences),
            preferences,
            context_product_ids,
        )

    primary = matches[0]
    name = product_value(primary, "name", language)
    notes = ", ".join(product_notes(primary, language))
    description = product_value(primary, "description", language)
    collection = product_value(primary, "collection", language)
    if not description and primary.get("documentation"):
        description = product_value(primary["documentation"], "description", language)
    if not notes and primary.get("documentation"):
        notes = ", ".join(product_notes(primary["documentation"], language))
    description = shorten_description(description)
    preference_text = preference_label(preferences, language)
    recipient_text = recipient_phrase(message, preferences, language)
    llm_answer = ""
    if not recommendation_mode and not (intent["price"] or intent["availability"] or intent["notes"]):
        llm_answer = hugging_face_answer(message, language, matches)

    if language == "ar":
        if intent["price"] and intent["notes"] and primary.get("price") is not None:
            answer = f"بالنسبة إلى {name}، أبرز النفحات هي: {notes or 'غير مذكورة في المصادر المتاحة'}. والسعر الظاهر في كتالوج منسَم المباشر هو {format_price(primary)}."
        elif intent["price"] and primary.get("price") is not None and intent["availability"]:
            answer = f"بالنسبة إلى {name}، السعر الظاهر هو {format_price(primary)}. {status_text(primary, language)}"
        elif intent["price"] and primary.get("price") is not None:
            answer = f"بالنسبة إلى {name}، السعر الظاهر في كتالوج منسَم المباشر هو {format_price(primary)}."
        elif intent["availability"]:
            answer = f"بالنسبة إلى {name}، {status_text(primary, language)}"
        elif intent["notes"]:
            answer = f"في {name} ستلاحظ: {notes or 'نفحات غير مذكورة في المصادر المتاحة'}."
        elif recommendation_mode:
            price_val = format_price(primary)
            price_str = f" السعر هو {price_val}." if price_val else ""
            answer = f"أرشح لك عطر {name}"
            if recipient_text:
                answer += f" {recipient_text}"
            if collection:
                answer += f" من مجموعة {collection}"
            answer += f".{price_str} متوفر اليوم.\n\nتخيل نفسك في وقت المغرب، والجو هادئ، وهذه الرائحة الدافئة تحيط بك كالعناق.\n\nالعديد من عملائنا اختاروا هذا العطر وعادوا لاقتنائه مجدداً، وأوصوا به في محيطهم.\n\nهل ترغب في أن أجهز لك الطلب، أم تود اقتراحاً آخر؟"
        else:
            answer = f"{name} قد يكون بداية جميلة"
            if collection:
                answer += f" من مجموعة {collection}"
            answer += f". {description}" if description else "."
            if notes:
                answer += f" أبرز النفحات: {notes}."
    else:
        if intent["price"] and intent["notes"] and primary.get("price") is not None:
            answer = f"For {name}, the key notes are {notes or 'not listed in the available sources'}. The live Mansam catalogue shows {format_price(primary)}."
        elif intent["price"] and primary.get("price") is not None and intent["availability"]:
            answer = f"For {name}, I found {format_price(primary)} in the live catalogue. {status_text(primary, language)}"
        elif intent["price"] and primary.get("price") is not None:
            answer = f"For {name}, the live Mansam catalogue shows {format_price(primary)}."
        elif intent["availability"]:
            answer = f"For {name}, {status_text(primary, language)}"
        elif intent["notes"]:
            answer = f"In {name}, you will notice {notes or 'notes not listed in the available sources'}."
        elif recommendation_mode:
            price_val = format_price(primary)
            price_str = f" The price is {price_val}." if price_val else ""
            answer = f"I recommend {name}"
            if recipient_text:
                answer += f" {recipient_text}"
            if collection:
                answer += f" from the {collection} collection"
            answer += f".{price_str} Available today.\n\nImagine yourself at Maghrib, the air calm, and this warm scent surrounds you like an embrace.\n\nMany of our clients chose this perfume and came back for it a second time, recommending it within their circle.\n\nWould you like me to prepare your order, or would you like another perfume suggestion?"
        else:
            answer = f"{name} could be a lovely place to start"
            if collection:
                answer += f" from the {collection} collection"
            answer += f". {description}" if description else "."
            if notes:
                answer += f" Key notes: {notes}."
    if llm_answer:
        answer = llm_answer

    return response_with_memory({
        "language": language,
        "answer": answer,
        "sources": product_source(primary),
        "productLinks": [
            {"name": primary.get("name", {}), "url": product_url(primary)}
        ] if product_url(primary) else [],
        "productIds": [str(item.get("id")) for item in matches],
        "catalogUpdatedAt": CATALOG_UPDATED_AT,
    }, preferences, [str(item.get("id")) for item in matches])


class MansamHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/health":
            body = json.dumps({"status": "ok", "service": "mansam-chatbot"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed_url.path in ("", "/"):
            self.send_response(302)
            self.send_header("Location", "/dream.html")
            self.end_headers()
            return

        if parsed_url.path in ("/tts", "/api/tts"):
            self.proxy_tts(parsed_url.query)
            return

        super().do_GET()

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/transcribe":
            self.transcribe_audio()
            return
        if parsed_url.path != "/api/chat":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 10000:
                raise ValueError("Request is too large")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            message = str(payload.get("message", "")).strip()
            language = str(payload.get("language", "")).lower()
            context_product_ids = payload.get("contextProductIds", [])
            if not isinstance(context_product_ids, list):
                context_product_ids = []
            conversation = payload.get("conversation", [])
            if not isinstance(conversation, list):
                conversation = []
            profile = payload.get("profile", {})
            if not isinstance(profile, dict):
                profile = {}
            if not message:
                raise ValueError("A message is required")
            refresh_live_catalog_if_needed()
            response = make_answer(message, language, context_product_ids[:3], conversation, profile)
            body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        except (ValueError, json.JSONDecodeError) as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(400)
        except Exception as error:
            print(f"Chat request failed: {type(error).__name__}: {error}")
            body = json.dumps({"error": "The fragrance guide is temporarily unavailable."}).encode("utf-8")
            self.send_response(503)
        else:
            self.send_response(200)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def transcribe_audio(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 12 * 1024 * 1024:
                raise ValueError("Audio payload must be between 1 byte and 12 MB")
            audio = self.rfile.read(content_length)
            if not HF_TOKEN:
                raise RuntimeError("HF_TOKEN is not configured for speech fallback")
            request = Request(
                ASR_API_URL,
                data=audio,
                headers={
                    "Authorization": f"Bearer {HF_TOKEN}",
                    "Content-Type": self.headers.get("Content-Type", "audio/webm"),
                },
                method="POST",
            )
            with urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
            transcript = str(result.get("text", "")).strip() if isinstance(result, dict) else ""
            if not transcript:
                raise RuntimeError("Speech service returned no transcript")
            body = json.dumps({"transcript": transcript}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
        except (ValueError, json.JSONDecodeError) as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(400)
        except Exception as error:
            print(f"Transcription request failed: {type(error).__name__}: {error}")
            body = json.dumps({"error": "Speech transcription is temporarily unavailable."}).encode("utf-8")
            self.send_response(503)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def proxy_tts(self, query_string):
        params = parse_qs(query_string)
        text = params.get("q", [""])[0].strip()
        language = params.get("tl", ["ar"])[0] or "ar"

        if not text:
            self.send_error(400, "Missing text")
            return

        upstream_query = urlencode({
            "ie": "UTF-8",
            "client": "tw-ob",
            "tl": language,
            "q": text
        })
        upstream_url = f"https://translate.google.com/translate_tts?{upstream_query}"
        request = Request(
            upstream_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }
        )

        try:
            with urlopen(request, timeout=15) as response:
                audio = response.read()
        except Exception as error:
            self.send_error(502, f"TTS request failed: {error}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(audio)))
        self.send_header("Cache-Control", "public, max-age=86400")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(audio)


if __name__ == "__main__":
    host = os.environ.get("MANSAM_HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    port = int(os.environ.get("MANSAM_PORT", os.environ.get("PORT", "5501")))
    url = f"http://{host}:{port}/dream.html"

    try:
        server = ThreadingHTTPServer((host, port), MansamHandler)
    except OSError:
        print(f"Port {port} is already in use.")
        print("Close the other local server or change the port in server.py.")
        input("Press Enter to exit...")
    else:
        print(f"Mansam site running at {url}")
        print("Keep this window open while testing Arabic language and speaker.")
        if os.environ.get("MANSAM_OPEN_BROWSER", "true").lower() == "true":
            webbrowser.open(url)
        server.serve_forever()
