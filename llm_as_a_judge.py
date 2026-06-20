import json
from parse_t4eu import extract_content as extract_content_t4eu
from parse_upr import extract_content as extract_content_upr


def build_user_prompt(article_text, extracted):
    extracted_payload = {
        "title": extracted.get("title"),
        "summary": extracted.get("summary"),
        "suitable_for_doctoral_students": extracted.get("suitable_for_doctoral_students"),
        "field": extracted.get("field"),
        "type": extracted.get("type"),
        "application": extracted.get("application"),
        "date_time": extracted.get("date_time"),
        "location": extracted.get("location"),
    }
    return (
        f"ARTICLE TEXT:\n\"\"\"\n{article_text}\n\"\"\"\n\n"
        f"EXTRACTED FIELDS (to evaluate):\n{json.dumps(extracted_payload, ensure_ascii=False, indent=2)}\n"
    )

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
            prompt = build_user_prompt(
                article_text=extract_content(soup_records[i]["link"]),
                extracted=llm_records[i]
            )
            print(prompt)
        except Exception as e:
            print(f"Error occurred while processing record {i}: {e}")