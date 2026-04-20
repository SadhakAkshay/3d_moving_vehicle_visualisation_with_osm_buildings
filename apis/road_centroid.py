from db import get_connection

def fetch_route_centroid(route_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
    id,
    ST_X(
        ST_Project(
            ST_StartPoint(ST_GeometryN(geom, 1))::geography,
            100,
            radians(heading_angle + 180)
        )::geometry
    ) AS longitude,

    ST_Y(
        ST_Project(
            ST_StartPoint(ST_GeometryN(geom, 1))::geography,
            100,
            radians(heading_angle + 180)
        )::geometry
    ) AS latitude,

    heading_angle,

    st_asgeojson(geom)::json

FROM dynamic_sld.cesium_road_dump
WHERE id = %s;
    """

    print(f"Executing query: {query} with route_id: {route_id}")

    cursor.execute(query, (route_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return None

    return {
        "id": result[0],
        "longitude": result[1],
        "latitude": result[2],
        "heading_angle": result[3],
        "route_geojson":result[4]
    }