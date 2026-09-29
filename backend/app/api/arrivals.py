from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Arrival
router = APIRouter(prefix="/arrivals", tags=["arrivals"])

class SaturationIn(BaseModel):
    saturated: bool

@router.get("")
def list_arrivals(line_id: int | None = None, db: Session = Depends(get_db)):
    rows = db.scalars(select(Arrival).options(joinedload(Arrival.trip)).order_by(Arrival.actual_arrive)).unique().all()
    out = []
    for r in rows:
        if line_id is not None and r.trip.line_id != line_id: continue
        out.append({"id": r.id, "trip_id": r.trip_id, "trip_no": r.trip.trip_no, "line_id": r.trip.line_id,
                    "stop_name": r.stop_name, "stop_seq": r.stop_seq, "actual_arrive": r.actual_arrive.isoformat(),
                    "saturated": r.saturated})
    return out

@router.patch("/{arrival_id}")
def set_saturation(arrival_id: int, body: SaturationIn, db: Session = Depends(get_db)):
    arrival = db.get(Arrival, arrival_id)
    if not arrival: raise HTTPException(404, "到站记录不存在")
    arrival.saturated = body.saturated
    db.commit()
    return {"id": arrival.id, "saturated": arrival.saturated}
