from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

import parse_t4eu
import parse_upr

client = QdrantClient(host="localhost", port=6333)

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

COLLECTION_NAME = "news_articles_2"
BASE_WEEKLY_COLLECTION_NAME = "weekly_news_articles_"

VECTOR_SIZE = 384

def update_weekly_collection():
    week_number = datetime.now().isocalendar()[1]
    global WEEKLY_COLLECTION_NAME
    WEEKLY_COLLECTION_NAME = BASE_WEEKLY_COLLECTION_NAME + str(week_number)


def ensure_collection(name):
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if name not in names:
        client.create_collection(
            collection_name=name,
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

def insert_article(article, names):
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
                    "total_chunks": len(chunks),
                    "link": article["link"]
                }
            )
        )

    for name in names:
        client.upsert(
            collection_name=name,
            points=points
        )

if __name__ == "__main__":
    update_weekly_collection()
    ensure_collection(COLLECTION_NAME)
    ensure_collection(WEEKLY_COLLECTION_NAME)

    articles = (
        parse_t4eu.get_articles() + 
        parse_upr.get_articles()
    )

    for article in articles:
        insert_article(article, [COLLECTION_NAME, WEEKLY_COLLECTION_NAME])
