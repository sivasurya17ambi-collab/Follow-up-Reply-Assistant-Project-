"""
Document Parsing and Chunking Module (Week 1 Requirement)
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import re
import json
import csv
import io
from typing import List, Dict, Any, Tuple
from pathlib import Path

class DocumentParser:
    """Parses text, markdown, json, and csv documents and splits into searchable chunks."""

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_and_metadata(self, filename: str, raw_content: str) -> Tuple[str, Dict[str, Any]]:
        """Extract clean text content and metadata based on file extension."""
        ext = Path(filename).suffix.lower()
        metadata: Dict[str, Any] = {
            "filename": filename,
            "ext": ext,
            "char_count": len(raw_content),
            "estimated_reading_minutes": max(1, round(len(raw_content.split()) / 200))
        }

        # Extract title or header if available
        first_line = raw_content.strip().split("\n")[0] if raw_content.strip() else filename
        metadata["title"] = first_line.replace("#", "").strip()[:80]

        # Extract attendees / participants if present in text
        attendees_match = re.search(r"Attendees?:\s*([^\n]+)", raw_content, re.IGNORECASE)
        if attendees_match:
            metadata["attendees"] = attendees_match.group(1).strip()

        # Extract meeting date if present
        date_match = re.search(r"Date:\s*([^\n]+)", raw_content, re.IGNORECASE)
        if date_match:
            metadata["meeting_date"] = date_match.group(1).strip()

        if ext == ".json":
            try:
                parsed_json = json.loads(raw_content)
                clean_text = json.dumps(parsed_json, indent=2)
                metadata["type"] = "structured_json"
                return clean_text, metadata
            except Exception:
                return raw_content, metadata

        elif ext == ".csv":
            try:
                reader = csv.reader(io.StringIO(raw_content))
                rows = list(reader)
                text_lines = []
                for row in rows:
                    text_lines.append(" | ".join(row))
                clean_text = "\n".join(text_lines)
                metadata["type"] = "tabular_csv"
                metadata["row_count"] = len(rows)
                return clean_text, metadata
            except Exception:
                return raw_content, metadata

        # Default text / markdown
        metadata["type"] = "meeting_transcript" if "meeting" in raw_content.lower() else "general_document"
        return raw_content, metadata

    def chunk_text(self, text: str, filename: str, base_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits text into overlapping chunks using hierarchical boundary splitting:
        paragraphs -> sentences -> words.
        Preserves complete thoughts without cutting mid-sentence whenever possible.
        """
        if not text or not text.strip():
            return []

        base_meta = base_metadata.copy() if base_metadata else {}
        
        # Clean text normalize line endings
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", normalized) if p.strip()]

        raw_chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            # If paragraph itself is longer than chunk_size, split by sentences
            if len(para) > self.chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                        current_chunk = (current_chunk + " " + sentence).strip()
                    else:
                        if current_chunk:
                            raw_chunks.append(current_chunk)
                        # Start new chunk with overlap if possible
                        if len(sentence) > self.chunk_size:
                            # Split by words
                            words = sentence.split()
                            temp = ""
                            for w in words:
                                if len(temp) + len(w) + 1 <= self.chunk_size:
                                    temp = (temp + " " + w).strip()
                                else:
                                    if temp:
                                        raw_chunks.append(temp)
                                    temp = w
                            current_chunk = temp
                        else:
                            current_chunk = sentence
            else:
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    current_chunk = (current_chunk + "\n\n" + para).strip()
                else:
                    if current_chunk:
                        raw_chunks.append(current_chunk)
                    current_chunk = para

        if current_chunk:
            raw_chunks.append(current_chunk)

        # Build chunk dictionaries with IDs and metadata
        result: List[Dict[str, Any]] = []
        clean_filename_slug = re.sub(r"[^\w\-_.]", "_", filename)

        for idx, chunk_content in enumerate(raw_chunks):
            chunk_dict = {
                "chunk_id": f"{clean_filename_slug}_chunk_{idx:03d}",
                "chunk_index": idx,
                "total_chunks": len(raw_chunks),
                "filename": filename,
                "content": chunk_content,
                "char_length": len(chunk_content),
                **base_meta
            }
            result.append(chunk_dict)

        return result
