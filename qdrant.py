from qdrant_client.models import VectorParams, Distance
from qdrant_client import QdrantClient

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
ensure_collection()

