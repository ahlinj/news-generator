import json

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

if __name__ == "__main__":
    llm_records = load_jsonl("data/extracted_llm_links_filtered_no_common_links_1_no_404s.jsonl")
    soup_records = load_jsonl("data/extracted_soup_links_filtered_and_img_5_no_404s.jsonl")
    print(f"LLM records: {len(llm_records)}")
    print(f"Soup records: {len(soup_records)}")