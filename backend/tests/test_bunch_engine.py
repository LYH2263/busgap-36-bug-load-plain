from datetime import datetime, timedelta
from app.services.bunch_engine import classify_gap, detect_bunching

def test_classify_bunching():
    assert classify_gap(2.0, 8.0, 3.0, 15.0)[0] == "bunching"

def test_classify_large():
    assert classify_gap(16.0, 8.0, 3.0, 15.0)[0] == "large_gap"

def test_classify_normal():
    assert classify_gap(8.0, 8.0, 3.0, 15.0)[0] == "normal"

def test_classify_bunching_saturated():
    status, suggestion = classify_gap(2.0, 8.0, 3.0, 15.0, later_saturated=True)
    assert status == "bunching_saturated"
    assert "满载串车" in suggestion
    assert "优先抽稀" in suggestion
    assert "缓行" not in suggestion

def test_classify_bunching_unsaturated_keeps_plain_wording():
    status, suggestion = classify_gap(2.0, 8.0, 3.0, 15.0, later_saturated=False)
    assert status == "bunching"
    assert "缓行" in suggestion
    assert "满载" not in suggestion

def test_large_gap_ignores_saturation():
    assert classify_gap(16.0, 8.0, 3.0, 15.0, later_saturated=True)[0] == "large_gap"

def test_normal_ignores_saturation():
    assert classify_gap(8.0, 8.0, 3.0, 15.0, later_saturated=True)[0] == "normal"

def test_detect_bunching_events():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2)},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 2
    assert events[0].status == "bunching"
    assert events[0].saturated is False
    assert events[1].status == "large_gap"

def test_detect_bunching_saturated_later_trip():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2), "saturated": True},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=4)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "bunching_saturated"
    assert events[0].saturated is True
    # T2→T3:后车 T3 未饱和,即使前车饱和也保持现网串车
    assert events[1].status == "bunching"
    assert events[1].saturated is False

def test_detect_large_gap_saturated_keeps_plain_wording():
    # 大间隔行不得被饱和逻辑改字,也不得变加重档
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=20), "saturated": True},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "large_gap"
    assert events[0].saturated is False
    assert "满载" not in events[0].suggestion and "饱和" not in events[0].suggestion

def test_detect_normal_saturated_keeps_normal():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=8), "saturated": True},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "normal"
    assert events[0].saturated is False

def test_recompute_follows_latest_saturation_toggle():
    # 改饱和勾选后再检必须跟新勾选,禁止按旧勾选出文案
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2), "saturated": True},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "bunching_saturated" and "优先抽稀" in events[0].suggestion
    # 取消勾选 -> 回到普通串车 + 缓行句
    arrivals[1]["saturated"] = False
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "bunching" and "缓行" in events[0].suggestion and "满载" not in events[0].suggestion
    # 重新勾选 -> 再次加重
    arrivals[1]["saturated"] = True
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "bunching_saturated" and "优先抽稀" in events[0].suggestion

def test_status_and_suggestion_always_same_tier():
    # 不变式:状态档与建议句必须落在同一档
    for saturated in (False, True):
        status, suggestion = classify_gap(2.0, 8.0, 3.0, 15.0, later_saturated=saturated)
        if saturated:
            assert status == "bunching_saturated"
            assert "满载串车" in suggestion and "优先抽稀" in suggestion and "缓行" not in suggestion
        else:
            assert status == "bunching"
            assert "缓行" in suggestion and "满载" not in suggestion
    status, suggestion = classify_gap(16.0, 8.0, 3.0, 15.0, later_saturated=True)
    assert status == "large_gap" and "满载" not in suggestion and "饱和" not in suggestion
    status, suggestion = classify_gap(8.0, 8.0, 3.0, 15.0, later_saturated=True)
    assert status == "normal" and "满载" not in suggestion

