import json
from parse_t4eu import extract_content as extract_content_t4eu
from parse_upr import extract_content as extract_content_upr

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def extract_content(url):
    if "transform4europe" in url:
        return extract_content_t4eu(url)
    elif "upr" in url:
        return extract_content_upr(url)
    
if __name__ == "__main__":
    llm_records = load_jsonl("data/extracted_llm_links_filtered_no_common_links_1_no_404s.jsonl")
    soup_records = load_jsonl("data/extracted_soup_links_filtered_and_img_5_no_404s.jsonl")
    n = len(llm_records)

    for i in range(n):
        try:
            print(f"{i}: {extract_content(soup_records[i]['link'])[:10]}")
        except Exception as e:
            print(f"Error occurred while processing record {i}: {e}")