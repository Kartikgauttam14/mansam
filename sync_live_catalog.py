"""Download the public Mansam catalogue used by the chatbot's RAG retriever."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SITE_URL = os.environ.get("MANSAM_SITE_URL", "https://uatuae.mansamworld.com").rstrip("/")
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "live-catalog.json"
PERFUME_OUTPUT_FILE = PROJECT_ROOT / "data" / "live-perfumes.json"
USER_AGENT = "Mansam-RAG-Catalog-Refresher/1.0"
PERFUME_LINES = {
    "Eau de Parfum 12ml",
    "Eau de Parfum 100ml",
    "Natural Oils and Blends",
    "Signature Blends (Attar)",
    "Maamoul Bukhoor",
    "Luban",
    "Dehab",
}


def fetch_json(path, timeout=45):
    request = Request(
        f"{SITE_URL}{path}",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def bilingual(en, ar):
    return {"en": en or "", "ar": ar or ""}


def split_notes(value):
    if isinstance(value, list):
        return [str(note).strip() for note in value if str(note).strip()]
    return [note.strip() for note in (value or "").split(",") if note.strip()]


def normalize_product(product, product_line):
    collection = product.get("collection") or {}
    emotion = product.get("emotion") or {}
    season = product.get("season") or {}
    stock = product.get("stockQuantity")
    return {
        "id": str(product.get("productId") or product.get("productCode") or product.get("productNameEn")),
        "productId": product.get("productId"),
        "code": product.get("productCode") or "",
        "name": bilingual(product.get("productNameEn") or product.get("productName"), product.get("productNameAr")),
        "meaning": bilingual(product.get("productMeaning"), product.get("productMeaning")),
        "description": bilingual(product.get("productDescriptionEn") or product.get("productDescription"), product.get("productDescriptionAr")),
        "notes": bilingual(split_notes(product.get("keyNotesEn") or product.get("keyNotes")), split_notes(product.get("keyNotesAr"))),
        "collection": bilingual(collection.get("collectionEn"), collection.get("collectionAr")),
        "emotion": bilingual(emotion.get("emotionEn"), emotion.get("emotionAr")),
        "productLine": bilingual(product_line.get("productLineNameEn") or product_line.get("productLineName"), product_line.get("productLineNameAr")),
        "gender": product.get("gender") or "",
        "season": season.get("seasonName") or "",
        "volume": product.get("productVolume") or "",
        "packaging": product.get("productPackaging") or "",
        "type": product.get("productType") or "",
        "price": product.get("productPrice"),
        "currency": "AED",
        "stockQuantity": stock,
        "available": bool(product.get("saleable")) and (stock is None or stock > 0),
        "bestseller": bool(product.get("bestseller")),
        "active": bool(product.get("active")),
        "sourceUrl": f"{SITE_URL}/productDetails/{product.get('productId', '')}",
    }


def get_line_products(product_line):
    query = urlencode({"productLineId": product_line["productLineId"], "languageCode": "002"})
    payload = fetch_json(f"/api/public/products?{query}")
    return [normalize_product(product, payload.get("productLine") or product_line) for product in payload.get("products", [])]


def main():
    product_lines = [line for line in fetch_json("/api/public/productlines") if line.get("active")]
    products = []
    failures = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(get_line_products, line): line for line in product_lines}
        for future in as_completed(futures):
            line = futures[future]
            try:
                products.extend(future.result())
                print(f"Synced {line['productLineNameEn']}")
            except Exception as error:
                failures.append(f"{line['productLineNameEn']}: {error}")
                print(f"Skipped {line['productLineNameEn']}: {error}")

    product_index = {}
    for product in products:
        product_index[product["id"]] = product

    catalog = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": SITE_URL,
        "productLines": [
            {
                "id": line["productLineId"],
                "name": bilingual(line.get("productLineNameEn"), line.get("productLineNameAr")),
                "description": bilingual(line.get("descriptionEn"), line.get("descriptionAr")),
            }
            for line in product_lines
        ],
        "products": list(product_index.values()),
        "failures": failures,
    }
    OUTPUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    perfume_products = [
        product for product in catalog["products"]
        if str(product.get("productLine", {}).get("en", "")).strip() in PERFUME_LINES
    ]
    PERFUME_OUTPUT_FILE.write_text(json.dumps({
        "generatedAt": catalog["generatedAt"],
        "source": SITE_URL,
        "productCount": len(perfume_products),
        "products": perfume_products,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(catalog['products'])} live products to {OUTPUT_FILE}")
    print(f"Saved {len(perfume_products)} live perfume products to {PERFUME_OUTPUT_FILE}")
    if failures:
        print(f"Completed with {len(failures)} skipped product lines.")


if __name__ == "__main__":
    main()
