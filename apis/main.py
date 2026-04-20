from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from road_centroid import fetch_route_centroid
from geojson_to_czml import generate_czml_from_db
from db import get_connection

app = FastAPI()

@app.get("/route-centroid/{route_id}")
def get_route_centroid(route_id: int):
    result = fetch_route_centroid(route_id)

    if not result:
        raise HTTPException(status_code=404, detail="Route not found")

    return result

class CzmlRequest(BaseModel):
    date: str
    road_id: int


@app.post("/generate-czml")
def create_czml(request: CzmlRequest):
    try:
        date = request.date
        road_id = request.road_id

        czml, geojson = generate_czml_from_db(get_connection(), date, road_id)

        return {
            "status": "success",
            "czml": czml,
            "geojson": geojson
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))