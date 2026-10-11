"""StoryGuard agent：提取声明 → 工具检索 → 判定 → 报告。"""
from .llm import LLM, extract_json
from .store import Hit
from .tools import Tools

EXTRACT_SYSTEM = (
    "你是长篇创作的设定一致性检查器。第一步：从给定的正文片段中，提取所有可被已有设定核验的事实声明。"
    "只提取与角色、时间线、世界观规则、伏笔相关的事实；不要提取文风、情绪、对话内容。"
)
EXTRACT_INSTRUCTION = (
    '请从下面的正文中提取设定声明，只输出 JSON 数组，每个元素形如 '
    '{"claim": "一句事实断言", "type": "character|timeline|rule|foreshadowing"}。'
    "没有可核验的声明就输出 []。"
)

JUDGE_SYSTEM = (
    "你是长篇创作的设定一致性检查器。第二步：判断一条声明是否与检索到的已有设定冲突。"
    "只依据【已有设定】判断，不要编造设定里没有的信息。"
)
JUDGE_INSTRUCTION = (
    '请判断下面【声明】与【已有设定】的关系，只输出一个 JSON 对象，形如 '
    '{"verdict": "conflict|consistent|unknown", "reason": "一句话理由", "sources": ["来源路径..."]}。'
    'verdict 含义：conflict=声明与设定矛盾；consistent=声明与设定一致；unknown=设定里查不到、无法判定。'
)


class StoryGuardAgent:
    def __init__(self, llm: LLM, tools: Tools):
        self.llm = llm
        self.tools = tools

    def check(self, draft_text: str) -> dict:
        """检查一段正文，返回结构化一致性报告。"""
        claims = self._extract_claims(draft_text)
        items = []
        for c in claims:
            hits = self.tools.dispatch(c["type"], c["claim"])
            judgement = self._judge(c["claim"], hits)
            items.append({
                "claim": c["claim"],
                "type": c["type"],
                "verdict": judgement.get("verdict", "unknown"),
                "reason": judgement.get("reason", ""),
                "sources": judgement.get("sources", []),
                "hits": [{"text": h.text, "source": h.source, "score": round(h.score, 3)} for h in hits],
            })
        result = self._summarize(items)
        result["items"] = items
        return result

    def _extract_claims(self, draft_text: str) -> list[dict]:
        messages = [
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content": f"{EXTRACT_INSTRUCTION}\n\n正文：\n{draft_text}"},
        ]
        raw = self.llm.chat(messages)
        data = extract_json(raw)
        if not isinstance(data, list):
            return []
        claims = []
        for item in data:
            if isinstance(item, dict) and item.get("claim"):
                claims.append({
                    "claim": str(item["claim"]),
                    "type": str(item.get("type", "character")),
                })
        return claims

    def _judge(self, claim: str, hits: list[Hit]) -> dict:
        context = "\n".join(
            f"- [{h.type}] {h.text} (来源: {h.source})" for h in hits
        ) or "（无检索结果）"
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": f"{JUDGE_INSTRUCTION}\n\n【声明】\n{claim}\n\n【已有设定】\n{context}"},
        ]
        raw = self.llm.chat(messages)
        data = extract_json(raw)
        if not isinstance(data, dict):
            return {}
        return {
            "verdict": data.get("verdict", "unknown"),
            "reason": data.get("reason", ""),
            "sources": data.get("sources", []),
        }

    def _summarize(self, items: list[dict]) -> dict:
        conflicts = sum(1 for i in items if i["verdict"] == "conflict")
        consistent = sum(1 for i in items if i["verdict"] == "consistent")
        unknown = sum(1 for i in items if i["verdict"] == "unknown")
        return {
            "summary": {
                "total": len(items),
                "conflicts": conflicts,
                "consistent": consistent,
                "unknown": unknown,
            },
        }


def format_report(result: dict) -> str:
    """把结构化报告渲染成 Markdown。"""
    s = result["summary"]
    lines = [
        "## 🛡️ 一致性检查报告",
        f"- 共核验 **{s['total']}** 条声明：🔴 冲突 {s['conflicts']} · 🟢 一致 {s['consistent']} · ⚪ 无法判定 {s['unknown']}",
        "",
    ]
    for i, item in enumerate(result.get("items", []), 1):
        icon = {"conflict": "🔴 冲突", "consistent": "🟢 一致", "unknown": "⚪ 无法判定"}.get(item["verdict"], "⚪")
        lines.append(f"### {i}. {icon} —— {item['claim']}")
        lines.append(f"*（类型 `{item['type']}`）*")
        if item.get("reason"):
            lines.append(f"> {item['reason']}")
        if item.get("sources"):
            lines.append(f"来源：`{', '.join(item['sources'])}`")
        lines.append("")
    return "\n".join(lines)
