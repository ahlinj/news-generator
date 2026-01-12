from qdrant_client.models import VectorParams, Distance
from qdrant_client import QdrantClient

import parse_t4eu
import parse_upr

client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "news_articles_1"
VECTOR_SIZE = 384

def ensure_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

def chunk_text(text, chunk_size=150, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks

def main():
    articles = (
        parse_t4eu.get_articles() +
        parse_upr.get_articles()
    )

    print(f"Loaded {len(articles)} articles")

    for article in articles:
        chunks = chunk_text(article["content"])
        print(f"{article['title']} -> {len(chunks)} chunks")

if __name__ == "__main__":
    main()
