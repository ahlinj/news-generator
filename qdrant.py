from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import uuid

import parse_t4eu
import parse_upr

client = QdrantClient(host="localhost", port=6333)

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

COLLECTION_NAME = "news_articles_2"
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

def insert_article(article):
    chunks = chunk_text(article["content"])
    vectors = model.encode(chunks)
    
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "title": article["title"],
                    "text": chunk,
                    "chunk_id": i,
                    "link": article["link"]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def main():
    ensure_collection()

    articles = (
        parse_t4eu.get_articles() +
        parse_upr.get_articles()
    )

    print(f"Loaded {len(articles)} articles")

    for article in articles:
        insert_article(article)
        print(f"Inserted article: {article['title']}")

if __name__ == "__main__":
    main()
