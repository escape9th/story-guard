from pathlib import Path

from guard.store import VectorStore
from guard.embedder import FakeEmbedder


def test_add_and_query_with_type_filter(tmp_path):
    emb = FakeEmbedder(dim=64)
    store = VectorStore(Path(tmp_path), ephemeral=True)
    texts = ["林澈 剑修 十七岁", "苏晚 药师", "灵气 复苏"]
    store.add(
        ids=["0", "1", "2"],
        texts=texts,
        embeddings=emb.embed(texts),
        metadatas=[
            {"source": "e/c.md", "work": "e", "type": "characters"},
            {"source": "e/c2.md", "work": "e", "type": "characters"},
            {"source": "e/r.md", "work": "e", "type": "rules"},
        ],
    )
    assert store.count() == 3

    qvec = emb.embed(["林澈 剑修"])[0]
    hits = store.query(qvec, top_k=2, type="characters")
    assert len(hits) == 2
    assert all(h.type == "characters" for h in hits)
    assert hits[0].text == "林澈 剑修 十七岁"
