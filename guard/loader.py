"""读取 data/<作品名>/<类型>/*.md 的设定文件，给每篇打上作品名和类型标签。"""
from dataclasses import dataclass
from pathlib import Path

# 支持的设定类型：文件夹名 → 类型
TYPES = {"characters", "timeline", "rules", "foreshadowing"}
SUPPORTED_SUFFIXES = {".md", ".txt"}


@dataclass
class Document:
    text: str
    work: str      # 作品名（第一层文件夹）
    type: str      # characters / timeline / rules / foreshadowing
    source: str    # 相对路径


def load_documents(data_dir: Path) -> list[Document]:
    docs = []
    if not data_dir.exists():
        return docs
    for work_dir in sorted(data_dir.iterdir()):
        if not work_dir.is_dir():
            continue
        work = work_dir.name
        for type_dir in sorted(work_dir.iterdir()):
            if not type_dir.is_dir() or type_dir.name not in TYPES:
                continue
            for path in sorted(type_dir.rglob("*")):
                if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                    try:
                        text = path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        text = path.read_text(encoding="gbk", errors="ignore")
                    rel = path.relative_to(data_dir).as_posix()
                    docs.append(Document(text=text, work=work, type=type_dir.name, source=rel))
    return docs
