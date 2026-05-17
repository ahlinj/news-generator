from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

import parse_t4eu
import parse_upr
import analysis

client = QdrantClient(host="localhost", port=6333)

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")

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

def insert_article(article, names, last_flag):
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

    if len(points) == 0:
        return

    for name in names:
        client.upsert(
            collection_name=name,
            points=points
        )
    
    if datetime.now().isoweekday() == 7 and last_flag:  # Sunday
        process_weekly_llm()

def process_weekly_llm():
    points = analysis.fetch_all_points(WEEKLY_COLLECTION_NAME)
    articles = analysis.group_articles(points)
    full_articles = analysis.reconstruct_articles(articles)

    for article in full_articles:
        extracted = analysis.call_llm(article["link"])
        extracted_data = analysis.extract_json(extracted)
        
        client.set_payload(
            collection_name=WEEKLY_COLLECTION_NAME,
            payload=extracted_data,
            points=article["point_ids"],
            wait=True
        )
        
        filtered_points = []
        offset = None

        while True:
            batch, offset = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="link",
                            match=MatchValue(value=article["link"])
                        )
                    ]
                ),
                limit=100,
                offset=offset,
                with_payload=False,
                with_vectors=False
            )
            
            filtered_points.extend(batch)
            
            if offset is None:
                break
        
        if filtered_points:
            point_ids_other = [p.id for p in filtered_points]
            
            client.set_payload(
                collection_name=COLLECTION_NAME,
                payload=extracted_data,
                points=point_ids_other,
                wait=True
            )

def create_dated_snapshot(collection_name: str):
    client.create_snapshot(collection_name)

if __name__ == "__main__":
    update_weekly_collection()
    ensure_collection(COLLECTION_NAME)
    ensure_collection(WEEKLY_COLLECTION_NAME)

    articles = (
        parse_t4eu.get_articles() + 
        parse_upr.get_articles()
    )

    if not articles:
        if datetime.now().isoweekday() == 7:
            process_weekly_llm()
    else:
        for article in articles:
            last_flag = (article == articles[-1])
            insert_article(article, [COLLECTION_NAME, WEEKLY_COLLECTION_NAME], last_flag)

    create_dated_snapshot(COLLECTION_NAME)
    create_dated_snapshot(WEEKLY_COLLECTION_NAME)
