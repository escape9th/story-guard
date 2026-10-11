# StoryGuard 🛡️ 设定一致性守护 Agent / Canon-Keeping Agent for Long-Form Writing

> 贴一段新写的正文，agent 自动抓出「设定声明」→ 调用工具检索已有设定 → 逐条判定冲突 → 输出带来源的防吃书报告。
> *Paste a draft; the agent extracts factual claims, retrieves your canon via tools, and flags conflicts — so you never break your own story.*

## 🔑 Keywords / 关键词

`AI Agent` · `Tool Calling` · `RAG` · `Retrieval-Augmented Generation` · `LLM` · `DeepSeek` · `Chroma` · `Vector Database` · `Embedding` · `bge-m3` · `Semantic Search` · `Consistency Checking` · `Novel Writing` · `Web Fiction` · `网文` · `设定管理` · `防吃书` · `伏笔追踪` · `Worldbuilding` · `LangChain` · `Streamlit` · `Python`

## 🤔 为什么做这个 / Why this exists

**市场痛点 / The pain point**：写长篇小说（尤其百万字的网文/剧本/游戏文案），作者根本记不住所有设定、伏笔、时间线，「**吃书**」（前后矛盾）是读者最反感的硬伤——而它往往到几十万字后才爆发，改起来伤筋动骨。

**为什么少人做 / Why few do it**：现有方案要么是**手动录入的 lorebook**（SillyTavern / NovelAI 的 Lorebook，得自己一条条填），要么是**被动问答 RAG**（问一句答一句）。**几乎没人做「主动检查新章节有没有吃书」的 agent。**

**为什么未来需求会涨 / Why demand is growing**：AI 让长内容生产成本骤降 → 内容更多、更长、更新更快 → **一致性管理的需求会爆炸**。这是「淘金热里卖铲子」。

## ✨ 它做什么 / What it does

作者贴一段新写的正文，agent 分四步：

1. **Extract 提取**：LLM 从正文提取所有「可核验的设定声明」（角色年龄/身份、事件、世界观规则、伏笔）。
2. **Retrieve 检索**：按声明类型，调用对应工具检索已有设定（角色 / 时间线 / 规则 / 伏笔）。
3. **Judge 判定**：LLM 对比声明 vs 检索到的设定，判定 🔴冲突 / 🟢一致 / ⚪无法判定，并附来源。
4. **Report 报告**：汇总成防吃书报告，冲突高亮，裁决权留给作者。

## 🏗 架构 / Architecture

```
data/<作品名>/{characters,timeline,rules,foreshadowing}/*.md
   → loader → indexer（切分 + bge-m3 向量化）→ Chroma 向量库

【agent 主循环】
正文 → ① extract（LLM 提取声明）
     → ② tools（按类型检索：角色/时间线/规则/伏笔）
     → ③ judge（LLM 判定一致/冲突/无法判定 + 来源）
     → ④ report（防吃书报告）
```

## 🧰 技术栈 / Tech Stack

| 层 Layer | 技术 Tech | 用途 Purpose |
|------|------|------|
| Language | Python ≥ 3.11 | 主体 |
| Agent 编排 | 手写 4 步主循环（extract→retrieve→judge→report） | 可控、可测 |
| LLM | DeepSeek（OpenAI 兼容 API） | 提取声明 + 判定 |
| Embedding | sentence-transformers + bge-m3 | 本地向量化 |
| Vector DB | Chroma | 按类型/作品过滤检索 |
| Chunking | langchain-text-splitters | 切分 |
| Web UI | Streamlit | 粘贴正文 → 看报告 |
| Testing | pytest | 13 个测试，用假实现无需 key |

## 🚀 快速开始 / Quick Start（Windows）

1. 复制 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY`
2. 双击 `setup.bat`（一次性装环境，清华镜像）
3. 双击 `run_app.bat` → 侧边栏「重建索引」→ 粘贴正文 → 「检查一致性」

> 第一次启动会下载 bge-m3 模型（约 2GB），之后离线运行。

## 📁 目录 / Structure

```
story-guard/
  guard/           # agent 核心（loader/embedder/store/tools/llm/agent/indexer）
  app.py           # Streamlit 网页
  config.py        # 配置（.env）
  data/            # 设定放这里（data/<作品名>/<类型>/*.md）
  tests/           # 13 个单元测试
  setup.bat / run_app.bat
```

## 🧪 测试 / Tests

```bash
python -m pytest -q
# 13 passed
```

用 `FakeLLM` + `FakeEmbedder` + 内存 Chroma 跑通全流程，不需要模型和 API key。

## 🗺 Roadmap / 路线图

- [ ] 伏笔回收追踪（记录"埋下"和"回收"的对应关系）
- [ ] 角色关系图谱 + 实体链接
- [ ] 批量检查整本书（按章节跑）
- [ ] 接入更多模型（Qwen / GLM / GPT）
- [ ] 把检索封装成 MCP server，供写作软件调用
