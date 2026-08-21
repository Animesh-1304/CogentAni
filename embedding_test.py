from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(
    host="localhost",
    port=6333
)

collection_name = "rag_embeddings"

texts = [
    "FastAPI is a Python framework used to build APIs quickly.",
    "Redis is an in-memory data store commonly used for caching.",
    "PostgreSQL is a relational database used to store structured data."
]

vectors = model.encode(texts).tolist()

client.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=index + 1,
            vector=vector,
            payload={"text": text}
        )
        for index, (vector, text) in enumerate(zip(vectors, texts))
    ]
)

print("Inserted", len(texts), "documents.")
query = "What is commonly used for caching?"

query_vector = model.encode(query).tolist()

results = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=1
).points

print("\nTop result:")
print("Score:", results[0].score)
print("Text:", results[0].payload["text"])