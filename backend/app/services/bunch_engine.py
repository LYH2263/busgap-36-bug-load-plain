"""Bus bunching: planned headway vs actual arrival gaps."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime

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

def classify_gap(gap_min: float, planned_headway_min: float, bunch_threshold: float, large_threshold: float,
                 later_saturated: bool = False) -> tuple[str, str]:
    if gap_min < bunch_threshold:
        return ("bunching", f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，建议后车缓行或抽稀。")
    if gap_min > large_threshold:
        if later_saturated:
            return ("large_gap",
                    f"间隔 {gap_min:.1f} 分钟超过大间隔阈值 {large_threshold}，后车已载客饱和，属满载串车，建议优先抽稀。")
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
            saturated = bool(cur.get("saturated", False))
            status, suggestion = classify_gap(gap_min, planned_headway_min, bunch_threshold, large_threshold,
                                              later_saturated=False)
            if saturated and status == "bunching":
                suggestion = f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，后车已载客饱和，属满载串车，建议优先抽稀。"
            events.append(GapEvent(stop, prev["trip_no"], cur["trip_no"], round(gap_min, 2), planned_headway_min,
                                   status, suggestion, False))
    return events

def events_to_dicts(events: list[GapEvent]) -> list[dict]:
    return [asdict(e) for e in events]

# topic helpers for report assembly

def saturated_label(status: str) -> str:
    if status == "bunching_saturated":
        return "bunching"
    return status

def strip_saturated_flag(events: list) -> list:
    out = []
    for e in events:
        if hasattr(e, "saturated"):
            try:
                e.saturated = False
            except Exception:
                pass
        out.append(e)
    return out

