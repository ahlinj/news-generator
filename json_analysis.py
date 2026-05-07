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

def compare_jsonl_lengths(path1, path2):
    with open(path1, 'r', encoding='utf-8') as f1, \
         open(path2, 'r', encoding='utf-8') as f2:
        pairs = list(zip([json.loads(l) for l in f1], [json.loads(l) for l in f2]))

    fields = ["image_links", "pdf_links", "mailto_links"]
    field_matches = {field: 0 for field in fields}
    mismatches_at = []

    for i, (r1, r2) in enumerate(pairs):
        for field in fields:
            c1 = len(set(normalize_link(l) for l in (r1.get(field) or [])))
            c2 = len(set(normalize_link(l) for l in (r2.get(field) or [])))
            
            if c1 == c2:
                field_matches[field] += 1
            else:
                mismatches_at.append((i, field))
                #print(f"Record {i} [{field}]: {c1} vs {c2} — '{r1.get('title')}'")

    total_per_field = len(pairs)
    print()
    for field in fields:
        matches = field_matches[field]
        print(f"{field:15} {matches}/{total_per_field} ({matches/total_per_field:.1%})")
    
    total_matches = sum(field_matches.values())
    total = len(pairs) * len(fields)
    print(f"\nOverall: {total_matches}/{total} ({total_matches/total:.1%})")
    #print(f"Mismatches at: {mismatches_at}")

def normalize_link(link):
    return link.replace("mailto:", "").strip().lower()

def compare_jsonl_elements(path1, path2):
    with open(path1, 'r', encoding='utf-8') as f1, \
         open(path2, 'r', encoding='utf-8') as f2:
        pairs = list(zip([json.loads(l) for l in f1], [json.loads(l) for l in f2]))

    fields = ["image_links", "pdf_links", "mailto_links"]
    field_matches = {field: 0 for field in fields}
    mismatches_at = []

    for i, (r1, r2) in enumerate(pairs):
        for field in fields:
            s1 = set(normalize_link(l) for l in (r1.get(field) or []))
            s2 = set(normalize_link(l) for l in (r2.get(field) or []))
            
            if s1 == s2:
                field_matches[field] += 1
            else:
                mismatches_at.append((i, field))
                missing = s1 - s2
                extra   = s2 - s1
                #print(f"Record {i} [{field}] — '{r1.get('title')}'")
                #for l in missing: print(f"  ✗ {l}")
                #for l in extra:   print(f"  + {l}")

    total_per_field = len(pairs)
    print()
    for field in fields:
        matches = field_matches[field]
        print(f"{field:15} {matches}/{total_per_field} ({matches/total_per_field:.1%})")
    
    total_matches = sum(field_matches.values())
    total = len(pairs) * len(fields)
    print(f"\nOverall: {total_matches}/{total} ({total_matches/total:.1%})")
    #print(f"Mismatches at: {mismatches_at}")

if __name__ == "__main__":
    compare_jsonl_lengths('data/extracted_soup_links_filtered_and_img_5_no_404s.jsonl','data/extracted_llm_links_filtered_no_common_links_8_no_404s.jsonl')
    compare_jsonl_elements('data/extracted_soup_links_filtered_and_img_5_no_404s.jsonl','data/extracted_llm_links_filtered_no_common_links_8_no_404s.jsonl')