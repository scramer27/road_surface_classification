import random
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

NUM_WINDOWS = 8  # how many windows to plot per class per config

# find all supervised csvs
supervised_files = sorted(Path('data/intermediary_data').glob('supervised_*.csv'))

# loop through different csvs (test configurations)
for csv_path in supervised_files:
    cfg_name = csv_path.stem.replace('supervised_', '') # drop supervised
    print(f"plot {cfg_name} configuration")

    # create dataframe
    data = pd.read_csv(csv_path)

    # loop through road_types
    for road_type in ['POTHOLE', 'NORMAL']:
        # find event IDs corresponding with road type
        event_ids = list(data[data['label'] == road_type]['event_id'].unique()) # makes a set
        random_ids = random.sample(event_ids, min(NUM_WINDOWS, len(event_ids))) # randomly choose IDs

        # asked gemini to create plots
        fig, axes = plt.subplots(len(random_ids), 4, figsize=(14, 2.5 * len(random_ids)))
        fig.suptitle(f"{road_type} windows — config {cfg_name}  (red = label press)", fontsize=12)

        # plot each event, along with label time and the full window showing the acceleration
        for i, event_id in enumerate(random_ids):
            # grab rows for this event and compute time relative to label press
            window = data[data['event_id'] == event_id].copy()
            label_time = pd.to_datetime(window['label_time'].iloc[0], utc=True, format='mixed')
            window['t'] = (pd.to_datetime(window['wall_clock'], utc=True, format='mixed') - label_time).dt.total_seconds()

            # plot each axis
            for j, col in enumerate(['ax', 'ay', 'az', 'atotal']):
                axes[i][j].plot(window['t'], window[col], linewidth=0.8)
                axes[i][j].axvline(0, color='red', linewidth=0.8, linestyle='--') # red line at label press
                axes[i][j].set_ylabel(col)
                if i == 0:
                    axes[i][j].set_title(col)
            axes[i][0].set_ylabel(f"{event_id.split('_')[-1]}\nax")

        fig.tight_layout()
plt.show()
print(f"done plotting")