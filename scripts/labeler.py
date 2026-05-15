import csv
import sys
import os
import tty
import termios
from datetime import datetime, timezone

WINDOW_POTHOLE   = 2.5  # seconds
WINDOW_SPEEDBUMP = 3.5  # seconds
WINDOW_NORMAL    = 5.0  # seconds

def now_utc(): # find current time
    return datetime.now(timezone.utc)

def format_time(dt): # format the time
    return dt.strftime("%H:%M:%S")

def get_key(): # from https://stackoverflow.com/questions/510357/how-to-read-a-single-character-from-the-user
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def log(msg):
    print(f"  [{format_time(now_utc())}] {msg}")

def print_keys(): # helper function for user
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
    events = [] # array of events collected
    collecting = False

    data_dir = 'data/input_data'
    os.makedirs(data_dir, exist_ok=True)
    existing = sorted([d for d in os.listdir(data_dir) if d.startswith('test_')])
    next_num = len(existing) + 1
    test_dir = os.path.join(data_dir, f'test_{next_num}')
    os.makedirs(test_dir, exist_ok=True)

    output_file = os.path.join(test_dir, f"labels_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")

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

            if key == 'p': # add a pothole
                events.append({"event_type": "POTHOLE", "wall_clock_time": t, "window_sec": WINDOW_POTHOLE})
                log(f"pothole  (+-{WINDOW_POTHOLE}s)")
            elif key == 's': # add a speedbump
                events.append({"event_type": "SPEEDBUMP", "wall_clock_time": t, "window_sec": WINDOW_SPEEDBUMP})
                log(f"speedbump  (+-{WINDOW_SPEEDBUMP}s)")
            elif key == 'n': # add a normal road segment
                events.append({"event_type": "NORMAL", "wall_clock_time": t, "window_sec": WINDOW_NORMAL})
                log(f"normal  ({WINDOW_NORMAL}s)")

        elif key == 'z': # remove last event
            if events:
                removed = events.pop()
                log(f"undo -- removed {removed['event_type']} at {format_time(removed['wall_clock_time'])}")
                if removed["event_type"] == "COLLECTION_START": # undo collection
                    collecting = False
                elif removed["event_type"] == "COLLECTION_STOP": # restart collection
                    collecting = True
            else:
                log("nothing to undo")

        elif key == 'h': # user asks for help
            print_keys()

        elif key == 'q': # end data takin
            log(f"saving {len(events)} events to {output_file}")
            break

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["event_type", "wall_clock_time", "window_sec"])
        writer.writeheader()
        writer.writerows(events)

    print(f"\n  saved -> {output_file}\n")

if __name__ == "__main__":
    main()
