import json
from parse_t4eu import extract_content as extract_content_t4eu
from parse_upr import extract_content as extract_content_upr

JUDGE_SYSTEM_PROMPT = """You are a evaluation judge for a automated newsletter generation. You will be given the text of a source article and a set of fields that a LLM extracted from that article. For EACH field below, decide whether the extracted value is factually correct and faithful to the article.
 
Rules:
- Answer "yes" if the extracted value is correct, faithful, and reasonably supported by the article.
- Answer "no" if the extracted value is wrong, unsupported, hallucinated, or contradicts the article.
- If a field is null/None in the extraction AND the article genuinely contains no such information, that is CORRECT -> "yes".
- If a field is null/None but the article DOES contain that information, that is INCORRECT -> "no".
- For "summary": check faithfulness and that it does not exceed 3 sentences and does not hallucinate facts.
- For "suitable_for_doctoral_students": judge whether the yes/no decision is a reasonable inference from the article's audience/content.
- For "type": judge whether classifying the article as "news" vs "event" matches its actual nature.
 
Respond ONLY with a JSON object (no markdown fences, no preamble, no extra commentary) with this exact shape, using ONLY "yes" or "no" for each verdict:
{
  "title": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "summary": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "suitable_for_doctoral_students": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "field": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "type": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "application.required": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "application.deadline": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "location.mode": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"},
  "location.place": {"verdict": "yes"|"no", "reasoning": "<one short sentence in English>"}
}
"""


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