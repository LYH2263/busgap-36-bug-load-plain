"""报告与时间轴组装时用的参与集辅助函数。"""
from __future__ import annotations

# scope_helpers_ready_36

def flatten_marks(marks: list[dict]) -> list[dict]:
    out: list[dict] = []
    for m in marks:
        item = dict(m)
        item.setdefault('visible', True)
        out.append(item)
    return out
