import streamlit as st

import config
from guard.agent import StoryGuardAgent, format_report
from guard.embedder import BgeM3Embedder
from guard.indexer import build_index
from guard.llm import DeepSeekLLM
from guard.store import VectorStore
from guard.tools import Tools

st.set_page_config(page_title="StoryGuard 防吃书", page_icon="🛡️", layout="wide")


@st.cache_resource
def get_deps():
    embedder = BgeM3Embedder(config.EMBED_MODEL_NAME)
    store = VectorStore(config.CHROMA_DIR)
    tools = Tools(embedder, store, config.TOP_K)
    llm = DeepSeekLLM(config.DEEPSEEK_API_KEY, config.DEEPSEEK_BASE_URL, config.DEEPSEEK_MODEL)
    agent = StoryGuardAgent(llm, tools)
    return agent, store, embedder


agent, store, embedder = get_deps()

st.title("🛡️ StoryGuard · 防吃书")
st.caption("粘贴一段新写的正文，agent 提取设定声明 → 检索已有设定 → 逐条判定是否冲突。")

with st.sidebar:
    st.header("设定库")
    if st.button("重建索引"):
        with st.spinner("读取设定 → 切分 → 向量化…"):
            store.reset()
            n = build_index(config.DATA_DIR, store, embedder, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        st.success(f"已建立 {n} 个片段")
    st.info(f"数据目录：`{config.DATA_DIR}`")
    if not config.DEEPSEEK_API_KEY:
        st.warning("未配置 DEEPSEEK_API_KEY，请在 `.env` 填写后重启。")

draft = st.text_area("粘贴新写的正文", height=200, placeholder="把这一章 / 这一段粘进来…")
if st.button("🛡️ 检查一致性", type="primary", disabled=not draft.strip()):
    with st.spinner("提取声明 → 检索 → 判定中…"):
        result = agent.check(draft)
    st.markdown(format_report(result))
    with st.expander("🔍 查看检索详情"):
        if not result.get("items"):
            st.write("没有提取到可核验的声明。")
        for i, item in enumerate(result.get("items", []), 1):
            st.markdown(f"**{i}. {item['claim']}**（类型 `{item['type']}`）")
            for h in item.get("hits", []):
                st.markdown(f"- `{h['source']}` · 相似度 {h['score']} — {h['text'][:60]}")
