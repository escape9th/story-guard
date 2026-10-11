from pathlib import Path

from guard.store import VectorStore
from guard.embedder import FakeEmbedder
from guard.tools import Tools
from guard.llm import FakeLLM
from guard.agent import StoryGuardAgent, format_report
from guard.indexer import build_index


def _make_agent(tmp_path):
    emb = FakeEmbedder(dim=64)
    store = VectorStore(tmp_path / "chroma", ephemeral=True)
    data_dir = tmp_path / "data"
    (data_dir / "example" / "characters").mkdir(parents=True)
    (data_dir / "example" / "rules").mkdir(parents=True)
    (data_dir / "example" / "characters" / "linche.md").write_text("林澈，十七岁，剑修，佩剑听雨。", encoding="utf-8")
    (data_dir / "example" / "rules" / "world.md").write_text("修行境界：练气、筑基、金丹、元婴。", encoding="utf-8")
    build_index(data_dir, store, emb, chunk_size=200, chunk_overlap=20)
    return Tools(emb, store, top_k=3)


def test_full_check_flow(tmp_path):
    tools = _make_agent(tmp_path)
    llm = FakeLLM([
        # 第一次调用：提取声明
        '[{"claim": "林澈二十岁", "type": "character"}, {"claim": "林澈是剑修", "type": "character"}]',
        # 第二次调用：判定第一条
        '{"verdict": "conflict", "reason": "设定为十七岁", "sources": ["example/characters/linche.md"]}',
        # 第三次调用：判定第二条
        '{"verdict": "consistent", "reason": "设定确为剑修", "sources": ["example/characters/linche.md"]}',
    ])
    agent = StoryGuardAgent(llm, tools)

    result = agent.check("林澈今年二十岁，他是个剑修。")

    assert result["summary"] == {"total": 2, "conflicts": 1, "consistent": 1, "unknown": 0}
    assert result["items"][0]["verdict"] == "conflict"
    assert result["items"][1]["verdict"] == "consistent"
    # 检索详情也应带上
    assert result["items"][0]["hits"]


def test_format_report_mentions_conflict():
    result = {
        "summary": {"total": 1, "conflicts": 1, "consistent": 0, "unknown": 0},
        "items": [{"claim": "林澈二十岁", "type": "character", "verdict": "conflict",
                   "reason": "设定为十七岁", "sources": ["example/characters/linche.md"]}],
    }
    text = format_report(result)
    assert "冲突" in text
    assert "林澈二十岁" in text
    assert "十七岁" in text
