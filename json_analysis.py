import json

def clean_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        records = [json.loads(line) for line in infile]
        cleaned = [r for r in records 
                   if '404 article not found (probably)' 
                   not in r.get('important_links')]

        outfile.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in cleaned)
        print(f"Removed {len(records) - len(cleaned)} records.")

if __name__ == "__main__":
    clean_jsonl('data/extracted_soup_links_filtered.jsonl', 'data/extracted_soup_links_filtered_no_404s.jsonl')