import requests
from qdrant_client import QdrantClient
from collections import defaultdict


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
    "important_links": string[]
    }}

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
    return response.json()


if __name__ == "__main__":
    points = fetch_all_points()
    articles = group_articles(points)
    full_articles = reconstruct_articles(articles)
    for article in full_articles:
        print(article["title"])
        print(article["text"])
        extracted = call_llm(article["text"])
        print(extracted)
        print("----------------------------------------------------------------------")