from pathlib import Path

from guard.store import VectorStore
from guard.embedder import FakeEmbedder
from guard.tools import Tools


def test_dispatch_routes_to_correct_type(tmp_path):
    emb = FakeEmbedder(dim=64)
    store = VectorStore(Path(tmp_path), ephemeral=True)
    store.add(
        ids=["c", "r"],
        texts=["林澈 剑修 十七岁", "境界 练气 筑基 金丹 元婴"],
        embeddings=emb.embed(["林澈 剑修 十七岁", "境界 练气 筑基 金丹 元婴"]),
        metadatas=[
            {"source": "e/c.md", "work": "e", "type": "characters"},
            {"source": "e/r.md", "work": "e", "type": "rules"},
        ],
    )
    tools = Tools(emb, store, top_k=2)

    hits = tools.dispatch("character", "林澈 剑修")
    assert all(h.type == "characters" for h in hits)
    assert hits[0].text == "林澈 剑修 十七岁"

    hits = tools.dispatch("rule", "境界")
    assert all(h.type == "rules" for h in hits)
