import os
import re
import uuid
from typing import Callable, List
import fitz  # PyMuPDF

def fetch_pdf_file(url: str, download_dir: str) -> str:
    import requests
    os.makedirs(download_dir, exist_ok=True)
    filename = url.split("/")[-1] or f"{uuid.uuid4().hex}.pdf"
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    path = os.path.join(download_dir, filename)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def _extract_text_from_pdf(path: str) -> str:
    texts = []
    with fitz.open(path) as doc:
        for page in doc:
            texts.append(page.get_text("text"))
    return "\n".join(texts)

def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    tokens = re.findall(r"\S+\s*", text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = "".join(tokens[i:i+chunk_size])
        chunks.append(chunk.strip())
        i += chunk_size - overlap
    return chunks

def ingest_folder(path: str, embeddings, store, progress_cb: Callable[[str], None] | None = None) -> int:
    total_chunks = 0
    for root, _, files in os.walk(path):
        for name in files:
            if name.lower().endswith(".pdf"):
                full = os.path.join(root, name)
                if progress_cb:
                    progress_cb(f"Parsing {full}")
                text = _extract_text_from_pdf(full)
                chunks = _chunk_text(text)
                if not chunks:
                    continue
                vecs = embeddings.encode(chunks)  # not used directly; Chroma can accept documents and perform its own encodes depending on setup
                ids = [f"{uuid.uuid4().hex}-{i}" for i in range(len(chunks))]
                metas = [{"source": full, "chunk_index": i} for i in range(len(chunks))]
                store.add(ids, chunks, metas)
                total_chunks += len(chunks)
    return total_chunks
