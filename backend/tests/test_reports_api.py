from tests.conftest import event


def test_report_grades_status_suggestion_label_together(client):
    """短间隔 + 后车(班次级)饱和:状态、建议句、标签必须同在满载串车加重档。"""
    res = client.post("/api/reports/run?line_id=1")
    assert res.status_code == 200
    ev = event(res.json()["events"], "T01", "T02", stop="起点站")
    assert ev["status"] == "bunching_saturated"
    assert ev["saturated"] is True
    assert ev["status_label"] == "满载串车"
    assert "满载串车" in ev["suggestion"]
    assert "优先抽稀" in ev["suggestion"]
    assert "缓行" not in ev["suggestion"]


def test_unsaturated_short_gap_stays_plain_bunching(client):
    """取消后车饱和后,短间隔回到普通串车档,建议为缓行。"""
    trips = {t["trip_no"]: t for t in client.get("/api/trips").json()}
    client.patch(f"/api/trips/{trips['T02']['id']}", json={"saturated": False})
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T01", "T02", stop="起点站")
    assert ev["status"] == "bunching"
    assert ev["saturated"] is False
    assert ev["status_label"] == "串车"
    assert "缓行" in ev["suggestion"]
    assert "满载" not in ev["suggestion"]


def test_toggle_retoggle_recomputes_each_time(client):
    """反复勾选:每次检测必须按最新勾选,不得吃改前缓存。"""
    trips = {t["trip_no"]: t for t in client.get("/api/trips").json()}
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T01", "T02", stop="起点站")
    assert ev["status"] == "bunching_saturated"

    client.patch(f"/api/trips/{trips['T02']['id']}", json={"saturated": False})
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T01", "T02", stop="起点站")
    assert ev["status"] == "bunching"

    client.patch(f"/api/trips/{trips['T02']['id']}", json={"saturated": True})
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T01", "T02", stop="起点站")
    assert ev["status"] == "bunching_saturated"


def test_large_gap_and_normal_never_moved_by_saturation(client):
    """大间隔/正常档即使后车勾选饱和,状态与建议句都不得改动。"""
    trips = {t["trip_no"]: t for t in client.get("/api/trips").json()}
    # 起点站 T02->T03 间隔 16 分属大间隔,把后车 T03 勾饱和
    client.patch(f"/api/trips/{trips['T03']['id']}", json={"saturated": True})
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T02", "T03", stop="起点站")
    assert ev["status"] == "large_gap"
    assert ev["saturated"] is False
    assert "满载" not in ev["suggestion"]
    assert "抽稀" not in ev["suggestion"]
    assert "前车减速或加发" in ev["suggestion"]

    # T03->T04 间隔 8 分属正常档,后车 T04 勾饱和也不变
    client.patch(f"/api/trips/{trips['T04']['id']}", json={"saturated": True})
    ev = event(client.post("/api/reports/run?line_id=1").json()["events"],
               "T03", "T04", stop="起点站")
    assert ev["status"] == "normal"
    assert "保持即可" in ev["suggestion"]


def test_arrival_level_saturation_single_stop_only(client):
    """班次级取消、仅在市民中心单站勾饱和:只加重该站,其他站保持普通串车。"""
    trips = {t["trip_no"]: t for t in client.get("/api/trips").json()}
    client.patch(f"/api/trips/{trips['T02']['id']}", json={"saturated": False})
    arrivals = client.get("/api/arrivals").json()
    t02_city = next(a for a in arrivals if a["trip_no"] == "T02" and a["stop_name"] == "市民中心")
    client.patch(f"/api/arrivals/{t02_city['id']}", json={"saturated": True})

    events = client.post("/api/reports/run?line_id=1").json()["events"]
    city = event(events, "T01", "T02", stop="市民中心")
    origin = event(events, "T01", "T02", stop="起点站")
    assert city["status"] == "bunching_saturated"
    assert origin["status"] == "bunching"


def test_suggestions_keep_severe_grade(client):
    """建议接口不得把满载串车盖回普通串车,且建议句与状态同档。"""
    tips = client.get("/api/reports/suggestions?line_id=1").json()["suggestions"]
    tip = event(tips, "T01", "T02", stop="起点站")
    assert tip["status"] == "bunching_saturated"
    assert tip["status_label"] == "满载串车"
    assert "优先抽稀" in tip["suggestion"]


def test_timeline_marks_share_report_grade(client):
    """时间轴标签/状态来自同一份检测结果,勾选改动后立即换档。"""
    marks = {m["trip_no"]: m for m in client.get("/api/reports/timeline?line_id=1&stop_name=起点站").json()["marks"]}
    assert marks["T02"]["status"] == "bunching_saturated"
    assert marks["T02"]["status_label"] == "满载串车"
    assert "优先抽稀" in marks["T02"]["suggestion"]
    assert marks["T03"]["status"] == "large_gap"

    trips = {t["trip_no"]: t for t in client.get("/api/trips").json()}
    client.patch(f"/api/trips/{trips['T02']['id']}", json={"saturated": False})
    marks = {m["trip_no"]: m for m in client.get("/api/reports/timeline?line_id=1&stop_name=起点站").json()["marks"]}
    assert marks["T02"]["status"] == "bunching"
    assert marks["T02"]["status_label"] == "串车"
