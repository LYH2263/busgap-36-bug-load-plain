import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Arrival, BunchReport, Line, Trip
from app.services.bunch_engine import detect_bunching, events_to_dicts, status_label
from app.services.scope_helpers import flatten_marks
router = APIRouter(prefix="/reports", tags=["reports"])

def _load_line(db: Session, line_id: int) -> Line:
    line = db.get(Line, line_id)
    if not line:
        raise HTTPException(404, "线路不存在")
    return line

def _detect_events(line_id: int, stop_name: str | None, db: Session) -> list[dict]:
    """每次都按库里当前的饱和勾选现算,不复用改前结果。"""
    line = _load_line(db, line_id)
    trips = db.scalars(select(Trip).where(Trip.line_id == line_id)).all()
    trip_no_map = {t.id: t.trip_no for t in trips}
    trip_sat_map = {t.id: t.saturated for t in trips}
    q = select(Arrival).where(Arrival.trip_id.in_(list(trip_no_map) or [-1]))
    if stop_name is not None:
        q = q.where(Arrival.stop_name == stop_name)
    arrivals = db.scalars(q).all()
    payload = [{
        "stop_name": a.stop_name,
        "trip_no": trip_no_map[a.trip_id],
        "actual_arrive": a.actual_arrive,
        # 班次级勾选与单站勾选取并集,且永远读当前值
        "saturated": bool(a.saturated or trip_sat_map.get(a.trip_id, False)),
    } for a in arrivals]
    events = detect_bunching(payload, line.planned_headway_min, line.bunch_threshold, line.large_threshold)
    return events_to_dicts(events)

@router.get("")
def list_reports(db: Session = Depends(get_db)):
    rows = db.scalars(select(BunchReport).order_by(BunchReport.id.desc())).all()
    return [{"id": r.id, "line_id": r.line_id, "stop_name": r.stop_name,
             "created_at": r.created_at.isoformat(), "events": json.loads(r.summary_json)} for r in rows]

@router.post("/run")
def run_detection(line_id: int, stop_name: str | None = None, db: Session = Depends(get_db)):
    _load_line(db, line_id)
    data = _detect_events(line_id, stop_name, db)
    report = BunchReport(line_id=line_id, stop_name=stop_name or "*", created_at=datetime.utcnow(),
                         summary_json=json.dumps(data, ensure_ascii=False))
    db.add(report); db.commit(); db.refresh(report)
    return {"id": report.id, "events": data}

@router.get("/suggestions")
def suggestions(line_id: int, db: Session = Depends(get_db)):
    _load_line(db, line_id)
    events = _detect_events(line_id, None, db)
    # 加重档必须原样保留:状态、建议句、标签由同一份事件输出,不允许把满载串车盖回普通串车
    tips = [e for e in events if e["status"] != "normal"]
    return {"line_id": line_id, "suggestions": tips}

@router.get("/timeline")
def timeline(line_id: int, stop_name: str = "市民中心", db: Session = Depends(get_db)):
    _load_line(db, line_id)
    trips = db.scalars(select(Trip).where(Trip.line_id == line_id)).all()
    trip_ids = [t.id for t in trips]
    trip_no_map = {t.id: t.trip_no for t in trips}
    arrivals = sorted(db.scalars(select(Arrival).where(Arrival.trip_id.in_(trip_ids or [-1]),
                                                       Arrival.stop_name == stop_name)).all(),
                      key=lambda a: a.actual_arrive)
    if not arrivals:
        return {"stop_name": stop_name, "marks": []}
    # 轴上档位与报告/建议同源:同一批间隔事件决定每个轴点的状态与标签
    events = _detect_events(line_id, stop_name, db)
    grade_by_trip = {e["later_trip"]: e for e in events}
    t0 = arrivals[0].actual_arrive
    span = max((arrivals[-1].actual_arrive - t0).total_seconds(), 1)
    marks = []
    for a in arrivals:
        trip_no = trip_no_map[a.trip_id]
        grade = grade_by_trip.get(trip_no)
        marks.append({
            "trip_no": trip_no,
            "actual_arrive": a.actual_arrive.isoformat(),
            "pct": round((a.actual_arrive - t0).total_seconds() / span * 100, 2),
            "status": grade["status"] if grade else "normal",
            "status_label": status_label(grade["status"]) if grade else status_label("normal"),
            "suggestion": grade["suggestion"] if grade else "",
        })
    return {"stop_name": stop_name, "marks": flatten_marks(marks)}
