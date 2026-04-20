A real-time, browser-based monitoring dashboard for garbage collection vehicles built on CesiumJS. Transforms raw GPS telemetry into an immersive 3D city experience with live building highlights, vehicle animation, and spatial analytics.

Project Overview
This project was built to solve a real operational problem in Nashik, Maharashtra — the Municipal Corporation had GPS trackers on garbage trucks but no live spatial monitoring layer. Officers had no way to verify, in real time, whether a vehicle had actually covered its assigned area.
The system provides:

🚛 Live vehicle animation driven by CZML from GPS logs
🏢 Dynamic building highlights — RED (allocated), GREEN (covered) — using OSM 3D Buildings
📊 Real-time stats — speed, odometer distance, area coverage %
🗺️ 2D / 3D mode toggle with seamless camera switching
🗑️ Dustbin GLB models placed on the roadside at collection stops
🗺️ WMS route overlays via GeoServer showing assigned and covered paths

⚙️ Tech Stack
Frontend->> CesiumJS 1.140, TurfJS v7, Vanilla JS
Backend->> FastAPI (Python)
Database->> PostgreSQL + PostGISMap 
Server->> GeoServer (WMS)
3D Models->> GLB (vehicle + dustbin)
Spatial Analysis->> TurfJS

✨ CesiumJS Features Used
Time-Dynamic Animation->> CZML drives GLB truck with VelocityOrientationProperty and CLAMP_TO_GROUND
Metadata Styling (3D Tiles)->> OSM Buildings styled per-feature via cesium#longitude / cesium#latitude properties
API Integration->> FastAPI endpoints for CZML generation; GeoServer WMS for route overlays
Geospatial Analysis->> TurfJS: linestring buffer, booleanPointInPolygon, odometer distance, roadside heuristic
Advanced Camera Control->> setView() follow in 2D; trackedEntity in 3D; flyTo() with complete() callback

🚀 Getting Started

Prerequisites

Python 3.9+
PostgreSQL with PostGIS
GeoServer running on localhost:8080
A Cesium Ion account (free) for the access token
