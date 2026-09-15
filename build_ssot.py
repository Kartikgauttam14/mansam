import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path(__file__).parent / "data" / "source-pdfs" / "Mansam Books" / "Mansam_SSOT_Master_v3_6.xlsx"
DATA_DIR = Path(__file__).parent / "data"
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def parse_workbook():
    with zipfile.ZipFile(SOURCE) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in item.iter("{%s}t" % NS["m"])) for item in root]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        sheets = {}
        for sheet in workbook.find("m:sheets", NS):
            target = targets[sheet.attrib["{%s}id" % NS["r"]]].replace("//", "/").lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            root = ET.fromstring(archive.read(target))
            rows = []
            for row in root.findall(".//m:sheetData/m:row", NS):
                values = {}
                for cell in row.findall("m:c", NS):
                    value = cell.find("m:v", NS)
                    text = "" if value is None else value.text or ""
                    if cell.attrib.get("t") == "s" and text:
                        text = shared[int(text)]
                    if cell.attrib.get("t") == "inlineStr":
                        text = "".join(t.text or "" for t in cell.iter("{%s}t" % NS["m"]))
                    if text != "":
                        values[re.match(r"[A-Z]+", cell.attrib["r"]).group(0)] = text
                if values:
                    rows.append(values)
            sheets[sheet.attrib["name"]] = rows
    return sheets


def records(rows):
    header_index = next((index for index, row in enumerate(rows[1:], start=1) if len(row) > 1), None)
    if header_index is None:
        return []
    headers = rows[header_index]
    return [{headers.get(key, key): value for key, value in row.items() if headers.get(key, key)} for row in rows[header_index + 1:]]


def sheet_training_rows(sheets):
    """Create one grounded training example for every non-empty workbook row."""
    training = []
    for sheet_name, raw_rows in sheets.items():
        for record in records(raw_rows):
            if not any(str(value).strip() for value in record.values()):
                continue
            training.append({
                "instruction": "Answer only from this Mansam SSOT workbook row. Do not invent facts; keep the answer concise and use the requested language.",
                "input": {"sheet": sheet_name, "record": record},
                "output": {"sourceSheet": sheet_name, "grounded": True},
            })
    return training


def text(row, key):
    return str(row.get(key, "")).strip()


def bilingual(row, english, arabic):
    return {"en": text(row, english), "ar": text(row, arabic)}


def split(value):
    return [part.strip() for part in re.split(r"[,/]", value or "") if part.strip()]


def product_links(sheets):
    links = {}
    for row in records(sheets["23_Product_Links"]):
        code = text(row, "SKU")
        url = text(row, "Full URL if different")
        if code and url:
            links.setdefault(code, url)
    return links


def build_products(sheets):
    products = []
    links = product_links(sheets)
    for row in records(sheets["02_Products_EDP"]):
        code = text(row, "SKU Code")
        products.append({
            "id": code, "code": code, "name": bilingual(row, "English Name", "Arabic Name (اسم العطر)"),
            "collection": bilingual(row, "Collection", "Collection (AR)"),
            "productLine": {"en": "Eau de Parfum 100ml", "ar": "ماء عطر 100 مل"},
            "gender": text(row, "Suitable For"),
            "description": bilingual(row, "Short Description", "Short Description (AR)"),
            "notes": {"en": split(" / ".join(text(row, key) for key in ("Top Notes", "Heart Notes", "Base Notes"))), "ar": split(" / ".join(text(row, key) for key in ("Top Notes (AR)", "Heart Notes (AR)", "Base Notes (AR)")))},
            "emotion": bilingual(row, "Emotion", "Emotion (AR)"), "season": text(row, "Season"), "volume": text(row, "Size"),
            "price": text(row, "Price AED"), "priceSar": text(row, "Price SAR"), "priceUsd": text(row, "Price USD"),
            "currency": "AED", "launchYear": text(row, "Year of Launch"),
            "keywords": bilingual(row, "Customer Keywords", "Customer Keywords (AR)"),
            "idealFor": bilingual(row, "Ideal For", "Ideal For (AR)"), "longevity": bilingual(row, "Longevity", "Longevity (AR)"),
            "sourceType": "ssot", "sourceSheet": "02_Products_EDP", "sourceUrl": links.get(code, ""),
        })
    product_sheets = {
        "13_Attars": ("Attar Name", "اسم العطّار", "Signature Blends (Attar)"),
        "14_Candles": ("Candle Name", "Candle Name", "Scented Candles"),
        "15_Maamoul_Bukhoor": ("Maamoul Bukhoor Name", "اسم معمول البخور", "Maamoul Bukhoor"),
        "16_Home_Diffusers": ("Diifuser Name", "اسم معطر الجو المنزلي", "Home Diffusers"),
    }
    for sheet, (name_en, name_ar, line) in product_sheets.items():
        for row in records(sheets[sheet]):
            code = text(row, "Product Code") or text(row, "KN Product Code")
            products.append({
                "id": code, "code": code, "name": bilingual(row, name_en, name_ar),
                "collection": bilingual(row, "Fragrance Family", "العائلة العطرية"),
                "productLine": {"en": line, "ar": line}, "gender": text(row, "Suitable For"),
                "description": bilingual(row, "Short Description", "الوصف المختصر"),
                "notes": {"en": split(" / ".join(text(row, key) for key in ("Top Notes", "Heart Notes", "Base Notes"))), "ar": split(" / ".join(text(row, key) for key in ("نوتات القمة", "نوتات القلب", "نوتات القاعدة")))},
                "price": text(row, "Price AED"), "priceSar": text(row, "Price SAR"), "priceUsd": text(row, "Price USD"),
                "currency": "AED", "volume": text(row, "Size") or text(row, "Net Weight"),
                "sourceType": "ssot", "sourceSheet": sheet, "sourceUrl": links.get(code, ""),
            })
    return products


if __name__ == "__main__":
    sheets = parse_workbook()
    sheet_records = {name: records(rows) for name, rows in sheets.items()}
    payload = {
        "sourceFile": SOURCE.name,
        "sourceSheetCount": len(sheets),
        "generatedAt": "2026-09-15",
        "products": build_products(sheets),
        "sheets": sheet_records,
        "sheetMeta": [
            {"name": name, "recordCount": len(items), "columns": sorted({key for item in items for key in item})}
            for name, items in sheet_records.items()
        ],
    }
    (DATA_DIR / "ssot-knowledge.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (DATA_DIR / "ssot-training.jsonl").open("w", encoding="utf-8") as output:
        for item in sheet_training_rows(sheets):
            output.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Generated {len(payload['products'])} products and {sum(len(items) for items in sheet_records.values())} workbook records from {len(sheets)} sheets")
