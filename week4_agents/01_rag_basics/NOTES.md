# RAG Basics

## What is RAG?

RAG stands for Retrieval-Augmented Generation.

Instead of asking an LLM to answer only from its trained knowledge,
RAG retrieves relevant information from an external knowledge source
and provides that information to the model as context.

## 4-Step RAG Pipeline

### 1. Load
Collect documents or text that we want the system to know about.

### 2. Chunk
Split large documents into smaller pieces called chunks.

### 3. Embed + Store
Convert each chunk into a vector using an embedding model
and store the vectors in Qdrant.

### 4. Retrieve + Generate
Convert the user's question into a vector, search Qdrant for
similar chunks, and provide the retrieved context to an LLM
to generate the final answer.

## Our Current Project

FastAPI
    ↓
Documents
    ↓
Embedding Model
    ↓
Qdrant
    ↓
Similarity Search
    ↓
Relevant chunks
    ↓
LLM (next stage)

## Technologies

- FastAPI — API layer
- Sentence Transformers — embeddings
- Qdrant — vector database
- Redis — caching/background-job support
- ARQ — background processing
- PostgreSQL — relational data