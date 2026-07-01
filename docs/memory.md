# Memory (ChromaDB)

Shared memory is stored in ChromaDB and accessed only via `core/memory.py`.

## Persist location

- Default: `data/chroma_db/`
- Override: `.env` → `CHROMA_PERSIST_DIR`

## Operations

- `store(key, value)`: add a text document with metadata key
- `search(query)`: semantic query returning top matches as combined text

