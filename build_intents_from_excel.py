import pandas as pd
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_FILE = PROJECT_ROOT / "data" / "source-pdfs" / "Mansam Books" / "Mansam_SSOT_Master_v3_6.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "excel_intents.json"

def process_objections(df):
    intents = []
    for i, row in df.iterrows():
        intent_id = str(row.get("Objection ID", "")).strip()
        if not intent_id or intent_id.startswith("Objection ID") or pd.isna(row.get("Objection ID")) or intent_id == "nan":
            continue
            
        ar_pattern = str(row.get("Trigger Phrase (Arabic)", "")).strip()
        en_pattern = str(row.get("Trigger Phrase (English)", "")).strip()
        
        ar_ack = str(row.get("Acknowledge (Arabic)", "")).strip()
        ar_ref = str(row.get("Reframe (Arabic, Saudi v2)", "")).strip()
        ar_q = str(row.get("Discovery Question (Arabic)", "")).strip()
        ar_resp = " ".join(filter(lambda x: x and x != "nan", [ar_ack, ar_ref, ar_q]))
        
        en_ack = str(row.get("Acknowledge (English)", "")).strip()
        en_ref = str(row.get("Reframe (English)", "")).strip()
        en_q = str(row.get("Discovery Question (English)", "")).strip()
        en_resp = " ".join(filter(lambda x: x and x != "nan", [en_ack, en_ref, en_q]))

        patterns = []
        if en_pattern and en_pattern != "nan": patterns.append(en_pattern)
        if ar_pattern and ar_pattern != "nan": patterns.append(ar_pattern)
            
        intents.append({
            "tag": intent_id,
            "patterns": patterns,
            "responses": [en_resp] 
        })
    return intents

def process_phrases(df):
    intents = []
    for i, row in df.iterrows():
        intent_id = str(row.get("Phrase ID", "")).strip()
        if not intent_id or intent_id.startswith("Phrase ID") or pd.isna(row.get("Phrase ID")) or intent_id == "nan":
            continue
            
        en_pattern = str(row.get("Use When", "")).strip()
        en_resp = str(row.get("English Translation", "")).strip()

        patterns = []
        if en_pattern and en_pattern != "nan": patterns.append(en_pattern)
            
        intents.append({
            "tag": intent_id,
            "patterns": patterns,
            "responses": [en_resp]
        })
    return intents

def main():
    if not SOURCE_FILE.exists():
        print(f"Error: {SOURCE_FILE} not found.")
        return
        
    xl = pd.ExcelFile(SOURCE_FILE)
    all_intents = []
    
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if len(df) > 1:
            df.columns = df.iloc[1]
            df = df[2:]
            
        if sheet == "04_Objections":
            all_intents.extend(process_objections(df))
        elif sheet == "03_Phrases":
            all_intents.extend(process_phrases(df))
            
    output = {"intents": all_intents}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(all_intents)} intents to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
