"""Bus bunching: planned headway vs actual arrival gaps."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime

# 状态档位:饱和只能把「短间隔普通串车」加重为满载串车,
# 大间隔 / 正常档不允许被饱和牵动。
STATUS_LABELS: dict[str, str] = {
    "bunching_saturated": "满载串车",
    "bunching": "串车",
    "large_gap": "大间隔",
    "normal": "正常",
}

def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, "正常")

@dataclass
class GapEvent:
    stop_name: str
    earlier_trip: str
    later_trip: str
    gap_min: float
    planned_headway_min: float
    status: str
    suggestion: str
    saturated: bool = False
    status_label: str = ""

def classify_gap(gap_min: float, planned_headway_min: float, bunch_threshold: float, large_threshold: float,
                 later_saturated: bool = False) -> tuple[str, str]:
    if gap_min < bunch_threshold:
        if later_saturated:
            return ("bunching_saturated",
                    f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，后车已载客饱和，属满载串车，建议优先抽稀。")
        return ("bunching", f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，建议后车缓行或抽稀。")
    if gap_min > large_threshold:
        # 大间隔档不读饱和:饱和勾选不得改大间隔的状态与建议句
        return ("large_gap", f"间隔 {gap_min:.1f} 分钟超过大间隔阈值 {large_threshold}，建议前车减速或加发。")
    return ("normal", f"间隔接近计划 {planned_headway_min:.1f} 分钟，保持即可。")

def detect_bunching(arrivals: list[dict], planned_headway_min: float, bunch_threshold: float, large_threshold: float) -> list[GapEvent]:
    by_stop: dict[str, list[dict]] = {}
    for a in arrivals:
        by_stop.setdefault(a["stop_name"], []).append(a)
    events: list[GapEvent] = []
    for stop, items in by_stop.items():
        items = sorted(items, key=lambda x: x["actual_arrive"])
        for i in range(1, len(items)):
            prev, cur = items[i - 1], items[i]
            gap_min = (cur["actual_arrive"] - prev["actual_arrive"]).total_seconds() / 60.0
            # 只看后车(cur)的当前勾选;前车饱和不影响该间隔档位
            saturated = bool(cur.get("saturated", False))
            status, suggestion = classify_gap(gap_min, planned_headway_min, bunch_threshold, large_threshold,
                                              later_saturated=saturated)
            events.append(GapEvent(stop, prev["trip_no"], cur["trip_no"], round(gap_min, 2), planned_headway_min,
                                   status, suggestion, status == "bunching_saturated", status_label(status)))
    return events

def events_to_dicts(events: list[GapEvent]) -> list[dict]:
    return [asdict(e) for e in events]
