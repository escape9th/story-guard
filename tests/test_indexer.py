from pathlib import Path

from guard.store import VectorStore
from guard.embedder import FakeEmbedder
from guard.indexer import build_index


def test_build_index_chunks_long_file(tmp_path):
    data_dir = tmp_path / "data"
    (data_dir / "example" / "characters").mkdir(parents=True)
    (data_dir / "example" / "characters" / "linche.md").write_text("林澈，十七岁，剑修。\n" * 50, encoding="utf-8")

    emb = FakeEmbedder(dim=64)
    store = VectorStore(tmp_path / "chroma", ephemeral=True)

    n = build_index(data_dir, store, emb, chunk_size=50, chunk_overlap=10)

    assert n > 1
    assert store.count() == n
