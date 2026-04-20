import gpxpy
import pandas as pd
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else "19-Apr-2026-1910.gpx"

with open(filepath, 'r') as f:
    gpx = gpxpy.parse(f)

points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append({
                'timestamp': point.time,
                'lat': point.latitude,
                'lon': point.longitude,
                'elevation': point.elevation
            })

df = pd.DataFrame(points)
print(df.to_string())
print(f"\nTotal points: {len(df)}")
