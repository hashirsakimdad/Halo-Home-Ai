"""ChromaDB vector memory — all memory reads/writes go through this module."""

import asyncio
import logging
import uuid
from functools import partial

import chromadb

from config.settings import CHROMA_COLLECTION, CHROMA_PERSIST_DIR

logger = logging.getLogger(__name__)


class MemoryClient:
    """Async wrapper around ChromaDB for shared agent memory."""

    def __init__(self, persist_dir: str | None = None, collection_name: str | None = None):
        """Initialize ChromaDB persistent client and collection."""
        self._persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self._collection_name = collection_name or CHROMA_COLLECTION
        self._client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = self._client.get_or_create_collection(name=self._collection_name)
        logger.info("Memory client ready: %s", self._collection_name)

    async def store(self, key: str, value: str) -> None:
        """Store a key-value pair in vector memory."""
        doc_id = f"{key}:{uuid.uuid4().hex[:8]}"
        await asyncio.to_thread(
            partial(
                self._collection.add,
                documents=[value],
                metadatas=[{"key": key}],
                ids=[doc_id],
            )
        )
        logger.debug("Stored memory key=%s id=%s", key, doc_id)

    async def search(self, query: str, n_results: int = 5) -> str:
        """Search memory by semantic similarity and return combined text."""
        try:
            results = await asyncio.to_thread(
                partial(
                    self._collection.query,
                    query_texts=[query],
                    n_results=n_results,
                )
            )
            documents = results.get("documents", [[]])[0]
            if not documents:
                return ""
            return "\n".join(documents)
        except Exception as exc:
            logger.error("Memory search failed: %s", exc)
            return ""
