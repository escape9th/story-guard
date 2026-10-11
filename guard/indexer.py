"""建索引：读设定 → 切分 → 向量化 → 入库。"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embedder import Embedder
from .loader import load_documents
from .store import VectorStore


def build_index(data_dir, store: VectorStore, embedder: Embedder,
                chunk_size: int = 500, chunk_overlap: int = 50) -> int:
    docs = load_documents(data_dir)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    )
    ids, texts, vecs, metas = [], [], [], []
    for d in docs:
        for j, chunk in enumerate(splitter.split_text(d.text)):
            chunk = chunk.strip()
            if not chunk:
                continue
            ids.append(f"{d.source}:{j}")
            texts.append(chunk)
            metas.append({"work": d.work, "type": d.type, "source": d.source})
    if ids:
        vecs = embedder.embed(texts)
        store.add(ids, texts, vecs, metas)
    return len(ids)
