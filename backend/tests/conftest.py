import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from app import database, main

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # main 在模块导入时已绑定 engine,两处都要换成内存库
    database.engine = engine
    main.engine = engine
    database.SessionLocal.configure(bind=engine)
    with TestClient(main.app) as c:
        yield c


def event(events, earlier, later, stop=None):
    hits = [e for e in events
            if e["earlier_trip"] == earlier and e["later_trip"] == later
            and (stop is None or e["stop_name"] == stop)]
    assert hits, f"event {earlier}->{later} not found"
    return hits[0]
