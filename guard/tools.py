"""检索工具：按设定类型检索（角色 / 时间线 / 规则 / 伏笔）。"""
from .embedder import Embedder
from .store import Hit, VectorStore

# 声明类型 → 检索类型 的映射（容忍 LLM 输出的同义词/中英文）
TOOL_MAP = {
    "character": "characters",
    "characters": "characters",
    "角色": "characters",
    "timeline": "timeline",
    "时间线": "timeline",
    "rule": "rules",
    "rules": "rules",
    "规则": "rules",
    "世界观": "rules",
    "foreshadowing": "foreshadowing",
    "伏笔": "foreshadowing",
}


class Tools:
    """agent 可调用的检索工具集。"""

    def __init__(self, embedder: Embedder, store: VectorStore, top_k: int = 4):
        self.embedder = embedder
        self.store = store
        self.top_k = top_k

    def search(self, query: str, type: str) -> list[Hit]:
        actual = TOOL_MAP.get(type, type)
        qvec = self.embedder.embed([query])[0]
        return self.store.query(qvec, self.top_k, type=actual)

    def search_characters(self, query: str) -> list[Hit]:
        return self.search(query, "characters")

    def search_timeline(self, query: str) -> list[Hit]:
        return self.search(query, "timeline")

    def search_rules(self, query: str) -> list[Hit]:
        return self.search(query, "rules")

    def search_foreshadowing(self, query: str) -> list[Hit]:
        return self.search(query, "foreshadowing")

    def dispatch(self, claim_type: str, query: str) -> list[Hit]:
        """根据声明类型，把查询分发到对应工具。"""
        return self.search(query, claim_type)
