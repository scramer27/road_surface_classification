# labeler.py
# Keyboard-driven road event labeler for data collection.
# Outputs a CSV of timestamped events to sync with accelerometer data.
#
# Keys:
#   SPACE  start/stop collection window
#   p      pothole
#   s      speed bump
#   n      normal road (optional baseline)
#   z      undo last event
#   h      show keys
#   q      quit and save

import csv
import sys
import tty
import termios
from datetime import datetime, timezone

WINDOW_POTHOLE   = 2.5  # seconds
WINDOW_SPEEDBUMP = 3.5
WINDOW_NORMAL    = 5.0

def now_utc():
    return datetime.now(timezone.utc)

def fmt_time(dt):
    return dt.strftime("%H:%M:%S")

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def log(msg):
    print(f"  [{fmt_time(now_utc())}] {msg}")

def print_keys():
    print()
    print("  SPACE  start/stop collection window")
    print("  p      pothole")
    print("  s      speed bump")
    print("  n      normal road")
    print("  z      undo last event")
    print("  h      show keys")
    print("  q      quit and save")
    print()

def main():
    events = []
    collecting = False
    output_file = f"labels_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    print(f"\nroad surface labeler")
    print(f"output: {output_file}")
    print_keys()

    while True:
        key = get_key()
        t = now_utc()

        if key == ' ':
            if not collecting:
                collecting = True
                events.append({"event_type": "COLLECTION_START", "wall_clock_time": t, "window_sec": ""})
                log("collection start")
            else:
                collecting = False
                events.append({"event_type": "COLLECTION_STOP", "wall_clock_time": t, "window_sec": ""})
                log("collection stop")

        elif key in ('p', 's', 'n'):
            if not collecting:
                log("not in collection window, ignored")
                continue

            if key == 'p':
                events.append({"event_type": "POTHOLE", "wall_clock_time": t, "window_sec": WINDOW_POTHOLE})
                log(f"pothole  (+-{WINDOW_POTHOLE}s)")
            elif key == 's':
                events.append({"event_type": "SPEEDBUMP", "wall_clock_time": t, "window_sec": WINDOW_SPEEDBUMP})
                log(f"speedbump  (+-{WINDOW_SPEEDBUMP}s)")
            elif key == 'n':
                events.append({"event_type": "NORMAL", "wall_clock_time": t, "window_sec": WINDOW_NORMAL})
                log(f"normal  ({WINDOW_NORMAL}s)")

        elif key == 'z':
            if events:
                removed = events.pop()
                log(f"undo -- removed {removed['event_type']} at {fmt_time(removed['wall_clock_time'])}")
                if removed["event_type"] == "COLLECTION_START":
                    collecting = False
                elif removed["event_type"] == "COLLECTION_STOP":
                    collecting = True
            else:
                log("nothing to undo")

        elif key == 'h':
            print_keys()

        elif key == 'q':
            log(f"saving {len(events)} events to {output_file}")
            break

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["event_type", "wall_clock_time", "window_sec"])
        writer.writeheader()
        writer.writerows(events)

    print(f"\n  saved -> {output_file}\n")

if __name__ == "__main__":
    main()
