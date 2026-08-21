import os

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured")


# OpenAI client
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Qdrant client
qdrant_client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "rag_openai"


# Create collection if it does not exist
collections = qdrant_client.get_collections().collections

if not any(
    collection.name == COLLECTION_NAME
    for collection in collections
):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE
        )
    )

    print(f"Created collection: {COLLECTION_NAME}")
else:
    print(f"Collection already exists: {COLLECTION_NAME}")


# Our documents
documents = [
    "FastAPI is a Python framework used for building APIs.",
    "Redis is an in-memory data store commonly used for caching.",
    "Qdrant is a vector database used for similarity search."
]


# Generate embeddings
points = []

for index, text in enumerate(documents, start=1):

    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    embedding = response.data[0].embedding

    points.append(
        PointStruct(
            id=index,
            vector=embedding,
            payload={
                "text": text
            }
        )
    )


# Store vectors in Qdrant
qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print("Documents stored in Qdrant.")


# Query
query = "What is Redis used for?"

query_response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)

query_embedding = query_response.data[0].embedding


# Similarity search
results = qdrant_client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding,
    limit=1
).points


print("\nTop result:")

for result in results:
    print("ID:", result.id)
    print("Score:", result.score)
    print("Text:", result.payload["text"])