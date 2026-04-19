import json

def clean_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        records = [json.loads(line) for line in infile]
        
        removed = [r for r in records 
                   if '404 article not found (probably)' 
                   in (r.get('all_links') or [])]
        
        cleaned = [r for r in records if r not in removed]

        outfile.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in cleaned)

def remove_null_lines(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        records = [r for line in f if (r := json.loads(line)) is not None]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in records)

def compare_jsonl(path1, path2):
    with open(path1, 'r', encoding='utf-8') as f1, \
         open(path2, 'r', encoding='utf-8') as f2:
        pairs = list(zip([json.loads(l) for l in f1], [json.loads(l) for l in f2]))

    fields = ["image_links", "pdf_links", "mailto_links"]
    total, mismatches = len(pairs) * len(fields), 0

    for i, (r1, r2) in enumerate(pairs):
        for field in fields:
            c1 = len(r1.get(field) or [])
            c2 = len(r2.get(field) or [])
            if c1 != c2:
                mismatches += 1
                print(f"Record {i} [{field}]: {c1} vs {c2} — '{r1.get('title')}'")

    print(f"\nSuccess: {total - mismatches}/{total} ({(total - mismatches) / total:.1%})")

if __name__ == "__main__":
    compare_jsonl('data/extracted_soup_links_filtered_and_img_no_404s.jsonl','data/extracted_llm_links_filtered_no_common_links_2_no_404s.jsonl')