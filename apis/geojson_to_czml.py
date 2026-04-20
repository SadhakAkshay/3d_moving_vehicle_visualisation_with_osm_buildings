import json
import psycopg2
from datetime import datetime

def fetch_geojson_from_db(conn, date_str, road_id):
    cursor = conn.cursor()

    query = """
    SELECT path_json 
    FROM dynamic_sld.actual_cesium_path 
    WHERE date(start_time)=%s AND road_id=%s
    """

    print(query)
    cursor.execute(query, (date_str, road_id))
    result = cursor.fetchone()

    if not result:
        raise Exception("No data found")

    geojson = result[0]

    # If stored as string → convert to dict
    if isinstance(geojson, str):
        geojson = json.loads(geojson)

    return geojson


def extract_time_from_geojson(geojson):
    features = geojson["features"]
    points = sorted(features, key=lambda f: f["properties"]["order"])

    start_time_str = points[0]["properties"]["timestamp"]
    end_time_str = points[-1]["properties"]["timestamp"]

    return start_time_str, end_time_str


def generate_czml_from_db(conn, date_str, road_id, height=0):

    # ✅ Step 1: Fetch GeoJSON
    geojson = fetch_geojson_from_db(conn, date_str, road_id)

    # ✅ Step 2: Extract time internally
    start_time_str, end_time_str = extract_time_from_geojson(geojson)

    start_time = datetime.fromisoformat(start_time_str.replace("Z", ""))
    end_time = datetime.fromisoformat(end_time_str.replace("Z", ""))

    total_duration = (end_time - start_time).total_seconds()

    features = geojson["features"]
    points = sorted(features, key=lambda f: f["properties"]["order"])

    waits = [f["properties"].get("wait", 0) for f in points]
    total_wait = sum(waits)

    # Normalize waits if too large
    if total_wait > total_duration:
        scale = total_duration / total_wait
        waits = [w * scale for w in waits]
        total_wait = sum(waits)

    num_segments = len(points) - 1
    movement_time = total_duration - total_wait
    time_per_segment = movement_time / num_segments if num_segments > 0 else 0

    current_time = 0
    carto = []

    for i, feature in enumerate(points):
        lon, lat = feature["geometry"]["coordinates"]
        wait = waits[i]

        carto.extend([round(current_time, 2), lon, lat, height])

        # wait
        if wait > 0:
            current_time += wait
            carto.extend([round(current_time, 2), lon, lat, height])

        # movement
        if i < len(points) - 1:
            current_time += time_per_segment

    # Final alignment
    last_lon, last_lat = points[-1]["geometry"]["coordinates"]
    carto.extend([round(total_duration, 2), last_lon, last_lat, height])

    czml = [
        {
            "id": "document",
            "version": "1.0",
            "clock": {
                "interval": f"{start_time_str}/{end_time_str}",
                "currentTime": start_time_str,
                "multiplier": 1
            }
        },
        {
            "id": "vehicle",
            "availability": f"{start_time_str}/{end_time_str}",
            "position": {
                "epoch": start_time_str,
                "cartographicDegrees": carto
            },
            "model": {
                "gltf": "GroundVehicle.glb",   # 🔥 your 3D model file
                "scale": 2.0,
                "minimumPixelSize": 64,
                "heightReference": "CLAMP_TO_GROUND"
            },
            "path": {
                "material": {
                    "polylineOutline": {
                        "color": {"rgba": [0, 0, 255, 255]},
                        "outlineColor": {"rgba": [255, 255, 255, 255]},
                        "outlineWidth": 2
                    }
                },
                "width": 4,
                "leadTime": 0,
                "trailTime": 0
            }
        }
    ]

    return czml,geojson