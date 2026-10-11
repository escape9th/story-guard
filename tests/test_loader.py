from pathlib import Path

from guard.loader import load_documents


def test_loads_by_type_and_work(tmp_path):
    work = tmp_path / "example"
    (work / "characters").mkdir(parents=True)
    (work / "timeline").mkdir()
    (work / "rules").mkdir()
    (work / "characters" / "linche.md").write_text("林澈，十七岁。", encoding="utf-8")
    (work / "timeline" / "events.md").write_text("三年前被逐出师门。", encoding="utf-8")
    (work / "rules" / "world.md").write_text("境界：练气筑基金丹元婴。", encoding="utf-8")
    (work / "ignore.txt").write_text("直接放在作品根目录，应被忽略", encoding="utf-8")

    docs = load_documents(tmp_path)

    assert len(docs) == 3
    by_source = {d.source: d for d in docs}
    assert by_source["example/characters/linche.md"].type == "characters"
    assert by_source["example/characters/linche.md"].work == "example"
    assert by_source["example/timeline/events.md"].type == "timeline"
    assert by_source["example/rules/world.md"].type == "rules"


def test_empty_dir(tmp_path):
    assert load_documents(tmp_path) == []
