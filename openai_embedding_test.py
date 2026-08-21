import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not configured")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.embeddings.create(
    model="openai/text-embedding-3-small",
    input="Redis is an in-memory data store commonly used for caching."
)

embedding = response.data[0].embedding

print("Embedding created successfully")
print("Vector size:", len(embedding))
print("First 5 values:", embedding[:5])