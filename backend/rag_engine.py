"""
RAG Engine with Chroma Vector Database (Week 1 & Week 2 Implementation)
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from backend.config import settings
from backend.document_parser import DocumentParser

class FastSemanticEmbeddingFunction(EmbeddingFunction):
    """
    Deterministic dense embedding function for Chroma.
    Uses subword n-grams and word tokens with feature hashing and L2 normalization.
    Guarantees 100% offline functionality without external network calls or PyTorch downloads.
    """
    def __init__(self, dim: int = 256):
        self.dim = dim

    def name(self) -> str:
        return "fast_semantic_hash_embedding"

    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    def _embed_single(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.dim

        vec = np.zeros(self.dim, dtype=np.float32)
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [w for w in clean.split() if len(w) > 1]

        # 1. Word token hashing
        for tok in tokens:
            h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign * 1.5

            # 2. Character 3-gram hashing for morphological matching
            if len(tok) >= 3:
                for i in range(len(tok) - 2):
                    ngram = tok[i:i+3]
                    nh = int(hashlib.md5(ngram.encode("utf-8")).hexdigest(), 16)
                    nidx = nh % self.dim
                    nsign = 1.0 if ((nh >> 8) & 1) else -1.0
                    vec[nidx] += nsign * 0.5

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed_single(doc) for doc in input]


class RAGEngine:
    """Manages document chunking, indexing in Chroma, and contextual retrieval."""

    def __init__(self, persist_dir: Optional[Path] = None, collection_name: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.parser = DocumentParser(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        self.embedding_function = FastSemanticEmbeddingFunction(dim=256)
        
        # Initialize Persistent Client
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Follow-up Reply Assistant Context Store"}
        )

    def add_document(self, filename: str, content: str, doc_type: str = "meeting_notes", extra_meta: Dict[str, Any] = None) -> int:
        """Parses, chunks, and indexes a single document into Chroma."""
        clean_text, meta = self.parser.extract_text_and_metadata(filename, content)
        meta["doc_type"] = doc_type
        if extra_meta:
            meta.update(extra_meta)

        chunks = self.parser.chunk_text(clean_text, filename, meta)
        if not chunks:
            return 0

        # Delete any existing chunks for this filename first to avoid duplicates
        self.delete_document(filename)

        ids = [c["chunk_id"] for c in chunks]
        docs = [c["content"] for c in chunks]
        metas = []
        for c in chunks:
            # Flatten metadata to simple types allowed by Chroma (str, int, float, bool)
            flattened = {
                "filename": str(c.get("filename", "")),
                "chunk_index": int(c.get("chunk_index", 0)),
                "doc_type": str(c.get("doc_type", doc_type)),
                "title": str(c.get("title", ""))[:100],
                "attendees": str(c.get("attendees", ""))[:120],
                "meeting_date": str(c.get("meeting_date", ""))[:50],
            }
            metas.append(flattened)

        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas
        )
        return len(chunks)

    def query_context(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves most relevant context chunks with similarity score and citations.
        Returns list of dicts with: snippet, source_doc, chunk_index, score, metadata.
        """
        if not query or not query.strip() or self.collection.count() == 0:
            return []

        actual_k = min(top_k, self.collection.count())
        results = self.collection.query(
            query_texts=[query],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"]
        )

        matched_chunks = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc_text, meta, dist in zip(docs, metas, distances):
                # Convert distance to normalized relevance score [0.0 to 1.0]
                relevance = max(0.0, min(1.0, round(1.0 - (dist / 2.0), 3)))
                matched_chunks.append({
                    "snippet": doc_text,
                    "source_doc": meta.get("filename", "unknown"),
                    "chunk_index": meta.get("chunk_index", 0),
                    "relevance_score": relevance,
                    "title": meta.get("title", ""),
                    "attendees": meta.get("attendees", ""),
                    "meeting_date": meta.get("meeting_date", "")
                })

        return matched_chunks

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """Returns summary list of all unique documents currently stored in the knowledge base."""
        count = self.collection.count()
        if count == 0:
            return []

        all_records = self.collection.get(include=["metadatas", "documents"])
        doc_map: Dict[str, Dict[str, Any]] = {}

        if all_records and "metadatas" in all_records:
            for meta, doc in zip(all_records["metadatas"], all_records["documents"]):
                fname = meta.get("filename", "unknown")
                if fname not in doc_map:
                    doc_map[fname] = {
                        "filename": fname,
                        "doc_type": meta.get("doc_type", "general"),
                        "chunks_count": 0,
                        "title": meta.get("title", fname),
                        "attendees": meta.get("attendees", ""),
                        "meeting_date": meta.get("meeting_date", ""),
                        "sample_preview": doc[:160] + "..." if len(doc) > 160 else doc
                    }
                doc_map[fname]["chunks_count"] += 1

        return list(doc_map.values())

    def delete_document(self, filename: str) -> bool:
        """Deletes all chunks belonging to a document."""
        try:
            existing = self.collection.get(where={"filename": filename})
            if existing and existing["ids"]:
                self.collection.delete(ids=existing["ids"])
                return True
        except Exception:
            pass
        return False

    def reset_knowledge_base(self):
        """Wipes and recreates the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def reindex_all_sample_documents(self, sample_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Admin refresh workflow: scans sample meetings directory and indexes all files."""
        dir_to_scan = sample_dir or settings.SAMPLE_DIR
        indexed_count = 0
        total_chunks = 0

        for file_path in dir_to_scan.glob("*.*"):
            if file_path.suffix.lower() in [".txt", ".md", ".json", ".csv"]:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    chunks_added = self.add_document(
                        filename=file_path.name,
                        content=content,
                        doc_type="meeting_transcript"
                    )
                    indexed_count += 1
                    total_chunks += chunks_added
                except Exception as e:
                    print(f"Error indexing {file_path.name}: {e}")

        return {
            "indexed_documents": indexed_count,
            "total_chunks": total_chunks,
            "collection_total": self.collection.count()
        }

# Global singleton RAG Engine instance
rag_engine = RAGEngine()
