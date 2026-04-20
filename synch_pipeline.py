import re
import pandas as pd
import gpxpy
from datetime import timezone, timedelta, datetime
import sys

acceleration_file  = sys.argv[1]
label_file = sys.argv[2]
gps_file    = sys.argv[3]
time_zone_diff   = int(sys.argv[4]) if len(sys.argv) > 4 else -4

# get accel start time from filename
match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', acceleration_file)
date_str, time_str = match.group(1), match.group(2).replace('-', ':')
accel_end = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
accel_end = accel_end.replace(tzinfo=timezone.utc) - timedelta(hours=time_zone_diff)

accel = pd.read_csv(acceleration_file)
accel_start = accel_end - timedelta(seconds=float(accel['time'].max()))
print(f"accel start: {accel_start}  end: {accel_end}  rows: {len(accel)}")

# sync labels
labels = pd.read_csv(label_file)
labels['wall_clock_time'] = pd.to_datetime(labels['wall_clock_time'], utc=True)
labels['accel_elapsed_sec'] = (labels['wall_clock_time'] - accel_start).dt.total_seconds()
print(labels['event_type'].value_counts().to_string())

# sync gps
with open(gps_file, 'r') as f:
    gpx = gpxpy.parse(f)

points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append({'timestamp': point.time, 'lat': point.latitude,
                           'lon': point.longitude, 'elevation': point.elevation})
gps = pd.DataFrame(points)
gps['accel_elapsed_sec'] = (gps['timestamp'] - accel_start).dt.total_seconds()
print(f"gps points: {len(gps)}")

labels.to_csv('synced_up_labels.csv', index=False)
gps.to_csv('synced_up_gps.csv', index=False)
print("created synced_labels.csv and synced_gps.csv")
