import json

import requests
from qdrant_client import QdrantClient
from collections import defaultdict
from bs4 import BeautifulSoup


COLLECTION_NAME = "news_articles_2"


client = QdrantClient(host="localhost", port=6333)

def fetch_all_points():
    points = []
    offset = None

    while True:
        batch, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=500,
            with_payload=True,
            with_vectors=False,
            offset=offset
        )

        points.extend(batch)

        if offset is None:
            break

    return points

def group_articles(points):
    articles = defaultdict(list)

    for p in points:
        payload = p.payload
        key = (payload["title"], payload["link"])
        articles[key].append(payload)

    return articles

def get_chunk_id(chunk):
    return chunk["chunk_id"]

def reconstruct_articles(grouped):
    full_articles = []

    for (title, link), chunks in grouped.items():
        sorted_chunks = sorted(chunks, key=get_chunk_id)

        texts = []
        for chunk in sorted_chunks:
            texts.append(chunk["text"])

        full_text = " ".join(texts)

        full_articles.append({
            "title": title,
            "link": link,
            "text": full_text
        })

    return full_articles


def call_llm(article_text):
    url = "http://hivecore.famnit.upr.si:6666/api/chat"

    prompt = f"""Extract structured information from the following article and return JSON with this schema:

    {{
    "title": string,
    "summary": string (max 3 sentences),
    "suitable_for_doctoral_students": "yes" | "no",
    "field": string,
    "type": "news" | "event",
    "application": {{
        "required": "yes" | "no",
        "link": string | null,
        "deadline": string | null
    }},
    "date_time": string | null,
    "location": {{
        "mode": "onsite" | "online" | "unknown",
        "place": string | null
    }},
    "important_links": string[] | null
    }}
    
    IMPORTANT:
    - Always extract the URL from the `href` attribute of <a> tags.
    - Do NOT extract the visible text between <a>...</a>.
    - Return the full absolute URL exactly as it appears in `href`.
    - Ignore links that are not real URLs (e.g., javascript:void, # anchors).

    Article:

    {article_text}
    """

    payload = {
            "model": "hf.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:UD-Q4_K_XL",
            "stream": False,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an information extraction system. Always return ONLY valid JSON. Do not include explanations or text outside JSON. Use the exact schema provided."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    response = requests.post(
        url,
        json=payload,
    )
    try:
        return response.json()
    except Exception as e:
        print("ERROR: Not valid JSON: ", e)
        print("RAW RESPONSE:", response.text)
        return None

def extract_json(response):
    try:
        content = response["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print("Invalid JSON:", e)
        return None
    
def save_jsonl(data, file_path):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def extract_links_soup(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", attrs={"data-elementor-type": "single-post"})
    
    if container is None:
        container = soup.find("div", attrs={"data-elementor-type": "single-page"})

    if container is None:
        container = soup.find("div", attrs={"class": "block-courses_details block-courses_details_full P30 bg-0 padding-top-15"})

    if container is None:
        return ["404 article not found (probably)"]
    return [a["href"] for a in container.find_all("a", href=True)]

if __name__ == "__main__":
    points = fetch_all_points()
    articles = group_articles(points)
    full_articles = reconstruct_articles(articles)
    i=0
    for article in full_articles:
        links = extract_links_soup(article["link"])
        i=i+1
        #extracted = call_llm(article["text"])
        #extracted_data = extract_json(extracted):
        result = {
            "title": article["title"],
            "link": article["link"],
            "important_links": links
        }
        print(i,"/", len(full_articles))
        save_jsonl(result, "data/extracted_soup_links.jsonl")
            