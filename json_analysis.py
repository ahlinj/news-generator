import json

def clean_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        records = [json.loads(line) for line in infile]
        
        removed = [r for r in records 
                   if '404 article not found (probably)' 
                   in r.get('important_links')]
        
        cleaned = [r for r in records if r not in removed]

        outfile.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in cleaned)

def remove_null_lines(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        records = [r for line in f if (r := json.loads(line)) is not None]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in records)

if __name__ == "__main__":
    clean_jsonl('data/extracted_soup_links_filtered.jsonl', 'data/extracted_soup_links_filtered_no_404s.jsonl')
    remove_null_lines('data/extracted_llm_links_filtered_no_common_links.jsonl','data/extracted_llm_links_filtered_no_common_links_no_404s.jsonl')