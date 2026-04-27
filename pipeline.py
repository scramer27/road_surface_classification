import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import gpxpy
import pandas as pd

# constants
TRIM_SEC = 5.0  # remove beginning and ending 5 sec

# pothole windows 
POTHOLE_WINDOWS = {
    'A': (2.5, 1.0), # 2.5 before, 1.0 after
    'B': (2.0, 0.5), # 2.0before, 0.5 after
}

# normal road windows
NORMAL_PRE_WINDOW  = 2.0
NORMAL_POST_WINDOW = 2.0

# contamination thresholds in seconds
CONTAM_THRESHOLDS = {
    '1': 2.5,
    '2': 3.0,
    '3': 3.5,
}

GPS_FIND = 2.0 # look for gps coordinate within 2 seconds

# load acceleration data (asked gemini how to encode times from end time)
def load_accel(path, timezone_offset):
    # accel filename includes end time of recording in local time
    match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', path.name)
    date_str = match.group(1)
    time_str = match.group(2).replace('-', ':')
    end_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    end_utc = end_local.replace(tzinfo=timezone.utc) - timedelta(hours=timezone_offset)

    df = pd.read_csv(path)
    start_utc = end_utc - timedelta(seconds=float(df['time'].max())) # find start time

    # build wall clock from elapsed seconds + derived start time
    df['wall_clock'] = pd.to_datetime(
        [start_utc + timedelta(seconds=float(t)) for t in df['time']], utc=True
    ).astype('datetime64[us, UTC]')

    return df, start_utc, end_utc

# load from label file (asked gemini how to load)
def load_labels(path):
    df = pd.read_csv(path)
    df['wall_clock'] = pd.to_datetime(df['wall_clock_time'], utc=True).astype('datetime64[us, UTC]')
    return df.sort_values('wall_clock').reset_index(drop=True) # create new indices

# load from gpx file (from gpx reader file)
def load_gps(path):
    with open(path, 'r') as f:
        gpx = gpxpy.parse(f)
    rows = []
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                rows.append({
                    'wall_clock': pt.time,
                    'lat':        pt.latitude,
                    'lon':        pt.longitude,
                    'elevation':  pt.elevation,
                })
    df = pd.DataFrame(rows)
    df['wall_clock'] = pd.to_datetime(df['wall_clock'], utc=True).astype('datetime64[us, UTC]')
    return df.sort_values('wall_clock').reset_index(drop=True) # create new indices

# process the data
def process_test(folder, timezone_offset):
    folder = Path(folder) # find location of folder
    accel_path = sorted(folder.glob('acceleration_*.csv'))[0]
    label_path = sorted(folder.glob('labels_*.csv'))[0]
    gps_path   = sorted(folder.glob('*.gpx'))[0]

    accel, accel_start, accel_end = load_accel(accel_path, timezone_offset)
    labels = load_labels(label_path)
    gps    = load_gps(gps_path)

    # trim 5s from each end then take the intersection
    win_start = max(
        accel_start + timedelta(seconds=TRIM_SEC),
        labels['wall_clock'].iloc[0]  + timedelta(seconds=TRIM_SEC),
        gps['wall_clock'].iloc[0]     + timedelta(seconds=TRIM_SEC),
    )
    win_end = min(
        accel_end - timedelta(seconds=TRIM_SEC),
        labels['wall_clock'].iloc[-1] - timedelta(seconds=TRIM_SEC),
        gps['wall_clock'].iloc[-1]    - timedelta(seconds=TRIM_SEC),
    )

    # clip everything to the window
    accel  = accel[(accel['wall_clock']   >= win_start) & (accel['wall_clock']   <= win_end)].copy()
    labels = labels[(labels['wall_clock'] >= win_start) & (labels['wall_clock']  <= win_end)].copy()
    gps    = gps[(gps['wall_clock']       >= win_start) & (gps['wall_clock']     <= win_end)].copy()

    accel['elapsed_sec'] = (accel['wall_clock'] - win_start).dt.total_seconds()
    accel['test']        = folder.name

    # find nearest GPS loc within 2 seconds for each acceleration row
    accel = pd.merge_asof(
        accel.sort_values('wall_clock'),
        gps[['wall_clock', 'lat', 'lon', 'elevation']],
        on='wall_clock',
        direction='nearest',
        tolerance=pd.Timedelta(seconds=GPS_FIND),
    )

    # find quantity of nonexistent gps locations after GPS loc search
    gps_nan = accel['lat'].isna().sum()

    # remove speedbumps and collection events (not enough data)
    events = labels[labels['event_type'].isin({'POTHOLE', 'NORMAL'})].copy()
    events['test'] = folder.name
    print(f"  labels : {events['event_type'].value_counts().to_dict()}")

    return accel, events

# helper to remove contaminated events
def find_contaminated_events(events, contam_sec):
    # find all timestamps touched by any cross-class pair within contamination threshold
    events = events.sort_values('wall_clock').reset_index(drop=True)
    times  = events['wall_clock'].tolist()
    event_labels   = events['event_type'].tolist()

    bad = set() # set of bad events
    left = 0
    for right in range(len(times)): # loop through times, if within contamination range, increment and append bad event
        while (times[right] - times[left]).total_seconds() > contam_sec: # checks if within contamination window
            left += 1
        for i in range(left, right):
            if event_labels[i] != event_labels[right]: # check if not the same event
                bad.add(times[i]) # if same event, add to bad
                bad.add(times[right])
    return bad

# find windows
def extract_windows(accel, clean_events, ph_pre, ph_post):
    collect = []
    for _, row in clean_events.iterrows(): # sort through cleaned events csv, and extract windows
        wall_time     = row['wall_clock']
        type_event = row['event_type'] # pothole or normal
        test_num  = row['test'] # origin of test

        # create event IDs
        id_event   = f"{test_num.replace(' ', '_')}_{type_event}_{pd.Timestamp(wall_time).strftime('%H%M%S')}"

        # define which window we are using, the given pothole window or the standard normal window
        pre, post = (ph_pre, ph_post) if type_event == 'POTHOLE' else (NORMAL_PRE_WINDOW, NORMAL_POST_WINDOW)

        # find appropriate acceleration rows
        block = accel[
            (accel['test']       == test_num) &
            (accel['wall_clock'] >= wall_time - pd.Timedelta(seconds=pre)) &
            (accel['wall_clock'] <= wall_time + pd.Timedelta(seconds=post))
        ].copy()
        
        # skip event if no accelation rows found
        if len(block) == 0:
            continue
        
        # additional information about event
        block['event_id']   = id_event
        block['label']      = type_event
        block['label_time'] = wall_time

        # add to collections
        collect.append(block)

    if not collect: # fixes error where every event got skipped and error got output
        return pd.DataFrame()

    # create full dataframe with necessary columns
    out = pd.concat(collect, ignore_index=True)
    cols = ['event_id', 'label', 'test', 'elapsed_sec', 'wall_clock',
            'ax', 'ay', 'az', 'atotal', 'lat', 'lon', 'elevation', 'label_time']
    return out[cols]

# main function
if __name__ == "__main__":
    folders = ['test 1', 'test 2', 'test 3', 'test 4']
    timezone_offset = -4
 
    print(f"Processing {len(folders)} test(s)  Timezone: UTC{timezone_offset:+d}")

    # process each test folder we have
    all_accel  = []
    all_events = []
    for folder in folders:
        accel, events = process_test(folder, timezone_offset)
        all_accel.append(accel)
        all_events.append(events)

    accel  = pd.concat(all_accel,  ignore_index=True)
    events = pd.concat(all_events, ignore_index=True)
    print(f"\n[combined]  rows: {len(accel):,}  labels: {events['event_type'].value_counts().to_dict()}")

    out_dir = Path('output')
    out_dir.mkdir(exist_ok=True)

    # unsupervised
    unsup_cols = ['test', 'elapsed_sec', 'wall_clock', 'ax', 'ay', 'az', 'atotal', 'lat', 'lon', 'elevation']
    unsup = accel[unsup_cols].dropna(subset=['lat', 'lon']).reset_index(drop=True) # drop rows with no GPS, reset index
    unsup.to_csv(out_dir / 'unsupervised.csv', index=False)
    print(f"\n[unsupervised] {len(unsup):,} rows -> unsupervised.csv  (dropped {len(accel)-len(unsup):,} no-GPS rows)") # show how many rows dropped

    # supervised all 6 configurations
    print(f"\nsupervised datasets")
    for win_key, (ph_pre, ph_post) in POTHOLE_WINDOWS.items(): # loop through pothole windows
        for thresh_key, thresh_sec in CONTAM_THRESHOLDS.items(): # loop through contamination thresholds
            cfg = f"{win_key}{thresh_key}" # create configuration corresponding to which of the two pothole windows and contamination threhsolds we are using

            # find contaminated events for given our contamination threshold, and remove
            contaminated_data   = find_contaminated_events(events, thresh_sec)
            cleaned_data = events[~events['wall_clock'].isin(contaminated_data)].reset_index(drop=True)

            # get windows for potholes and normal roads
            windows = extract_windows(accel, cleaned_data, ph_pre, ph_post)
            if len(windows) > 0: # check if windows are successfully populated
                windows.to_csv(out_dir / f"supervised_{cfg}.csv", index=False)
            
            # explains how many events dropped during cleaning process for each configuration
            print(f"  {cfg}  dropped={len(events)-len(cleaned_data)}  kept={cleaned_data['event_type'].value_counts().to_dict()}")

    print(f"\n output files created")
