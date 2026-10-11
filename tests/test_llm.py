from guard.llm import extract_json


def test_extract_plain_array():
    assert extract_json('[{"claim": "x", "type": "character"}]') == [{"claim": "x", "type": "character"}]


def test_extract_with_fence_and_noise():
    text = '好的，结果如下：\n```json\n[{"a": 1}]\n```\n以上。'
    assert extract_json(text) == [{"a": 1}]


def test_extract_object():
    assert extract_json('{"verdict": "conflict", "reason": "年龄矛盾"}') == {"verdict": "conflict", "reason": "年龄矛盾"}


def test_extract_none():
    assert extract_json("没有结果") is None
