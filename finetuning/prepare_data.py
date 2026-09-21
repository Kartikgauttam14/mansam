"""Build draft evidence-grounded examples; no network access or training."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'data'
SYSTEM = ('You are the Mansam AI fragrance assistant. Answer the current question using only '
          'the supplied evidence. Do not enforce a questionnaire. Never invent product facts. '
          'Return only JSON with answer and productIds. Use the customer language. '
          'If evidence is missing, say so; do not guess.')


def main():
    products = json.loads((ROOT / 'data/live-catalog.json').read_text(encoding='utf-8'))['products']
    splits = {'train': [], 'validation': []}
    groups = {'train': set(), 'validation': set()}
    for product in products:
        name_en = product.get('name', {}).get('en', '').strip()
        if not name_en:
            continue
        group = re.sub(r'[^a-z0-9]', '', name_en.lower())
        split = 'validation' if int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) % 5 == 0 else 'train'
        groups[split].add(group)
        for language in ('en', 'ar'):
            name = product.get('name', {}).get(language, '').strip()
            if not name:
                continue
            evidence = {key: product.get(key) for key in ('id', 'name', 'notes', 'volume', 'price', 'currency', 'gender')}
            tasks = []
            price = product.get('price')
            if price is not None:
                tasks.append((f'What is the price of {name}?' if language == 'en' else f'ما سعر {name}؟',
                              f'{name}: {price} {product.get("currency", "AED")}.'))
            notes = product.get('notes', {}).get(language, [])
            notes = ', '.join(notes) if isinstance(notes, list) else str(notes or '')
            tasks.append((f'What are the notes in {name}?' if language == 'en' else f'ما نفحات {name}؟',
                          f'{name}: {notes}.' if notes else
                          ('The supplied catalogue does not list this product’s notes.' if language == 'en'
                           else 'لا يذكر الكتالوج المقدم نفحات هذا المنتج.')))
            for question, answer in tasks:
                splits[split].append({
                    'prompt': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(
                        {'message': question, 'product_evidence': [evidence]}, ensure_ascii=False)}],
                    'completion': [{'role': 'assistant', 'content': json.dumps(
                        {'answer': answer, 'productIds': [str(product['id'])]}, ensure_ascii=False)}],
                })
    assert not groups['train'] & groups['validation']
    OUT.mkdir(exist_ok=True)
    for split, rows in splits.items():
        assert rows
        with (OUT / f'{split}.jsonl').open('w', encoding='utf-8') as output:
            for row in rows:
                json.loads(row['completion'][0]['content'])
                output.write(json.dumps(row, ensure_ascii=False) + '\n')
    report = {'status': 'draft; not human-reviewed', 'examples': {k: len(v) for k, v in splits.items()},
              'product_name_groups': {k: len(v) for k, v in groups.items()},
              'split': 'deterministic by normalized product name; size variants stay together',
              'limitations': ['Template-derived examples, not real customer conversations',
                              'Does not yet cover multi-turn preference changes or retrieval planning',
                              'Human review and behavioral examples needed before production training']}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
