"""Vectorstore abstractions for weightless Shadow Seeds."""

from shadowseed.vectorstore.base import VectorStore
from shadowseed.vectorstore.memory import InMemoryVectorStore

__all__ = ["VectorStore", "InMemoryVectorStore"]
