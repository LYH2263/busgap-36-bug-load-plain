from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Trip
router = APIRouter(prefix="/trips", tags=["trips"])

class SaturationIn(BaseModel):
    saturated: bool

@router.get("")
def list_trips(line_id: int | None = None, db: Session = Depends(get_db)):
    q = select(Trip).order_by(Trip.planned_depart)
    if line_id is not None: q = q.where(Trip.line_id == line_id)
    return [{"id": r.id, "line_id": r.line_id, "trip_no": r.trip_no,
             "planned_depart": r.planned_depart.isoformat(), "vehicle_no": r.vehicle_no,
             "saturated": r.saturated}
            for r in db.scalars(q).all()]

@router.patch("/{trip_id}")
def set_saturation(trip_id: int, body: SaturationIn, db: Session = Depends(get_db)):
    trip = db.get(Trip, trip_id)
    if not trip: raise HTTPException(404, "班次不存在")
    trip.saturated = body.saturated
    db.commit()
    return {"id": trip.id, "trip_no": trip.trip_no, "saturated": trip.saturated}
