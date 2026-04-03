import requests
from qdrant_client import QdrantClient


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
    print(len(points))

