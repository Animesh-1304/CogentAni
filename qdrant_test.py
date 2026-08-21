from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


client = QdrantClient(
    url="http://localhost:6333"
)


points = [
    PointStruct(
        id=1,
        vector=[0.9, 0.1, 0.2, 0.1],
        payload={
            "text": "FastAPI is a Python framework for building APIs."
        }
    ),

    PointStruct(
        id=2,
        vector=[0.1, 0.9, 0.2, 0.1],
        payload={
            "text": "Redis is an in-memory data store commonly used for caching."
        }
    ),

    PointStruct(
        id=3,
        vector=[0.1, 0.2, 0.9, 0.8],
        payload={
            "text": "ARQ is a Python job queue that uses Redis for background tasks."
        }
    )
]


client.upsert(
    collection_name="rag_documents",
    points=points
)
query_vector = [0.1, 0.8, 0.2, 0.1]
results = client.query_points(
    collection_name="rag_documents",
    query=query_vector,
    limit=1
).points


print("\nTop result:")

for result in results:
    print("ID:", result.id)
    print("Score:", result.score)
    print("Text:", result.payload["text"])