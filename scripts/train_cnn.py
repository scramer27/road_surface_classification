import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader
from torchinfo import summary
from src.models import *
from src.helpers import *

# constants
ACCELS = ['ax', 'ay', 'az', 'atotal']
CLASSES = ['NORMAL', 'POTHOLE']
WINDOW_LENGTHS = {'A': 350, 'B': 250, 'C' : 150}

# use better devices if available
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print(f"Using device: {device}")


if __name__ == "__main__":
    torch.manual_seed(42)
    np.random.seed(42)

    config_files = sorted([f'/content/supervised_{c}.csv' for c in ['B3','C3']])
    cost_matrix = torch.tensor([[0, 200], [400, 0]], dtype=torch.float32).to(device)

    window_length = WINDOW_LENGTHS['C']

    df = pd.read_csv('data/intermediary_data/supervised_C3.csv')

    # split events using random integer
    event_ids = df['event_id'].unique()
    idx = torch.randperm(len(event_ids)).tolist() # fixed error where slicing wasn't working
    split = int(0.8 * len(idx))

    train_ids = event_ids[idx[:split]]
    val_ids = event_ids[idx[split:]]

    # create dataloaders, using dataset objects like miniproject
    train_loader = DataLoader(RoadSurfaceDataset(df[df['event_id'].isin(train_ids)], window_length, device, augment = True), # isin mask to check fo rcorrect event_ids
                                batch_size=16, shuffle=True)
    val_loader   = DataLoader(RoadSurfaceDataset(df[df['event_id'].isin(val_ids)], window_length, device, augment = False), # isin mask to check fo rcorrect event_ids
                                batch_size=16, shuffle=False)

    # create model and training loop
    model = RoadSurfaceCNN().to(device)
    opt   = torch.optim.Adam(model.parameters(), lr=5e-4)
    best_f1 = 0.0 # used f1, as we have an imbalanced dataset, accuracy may just piggyback off of existing class imbalance

    print(summary(model, input_size = next(iter(train_loader))[0].shape, device = device))

    for epoch in range(100):
        model.train()
        for X_batch, y_batch in train_loader:
            opt.zero_grad()
            loss = binary_cross_entropy(model(X_batch), y_batch.reshape(-1,1))
            loss.backward()
            opt.step()

        model.eval()
        val_acc, val_ec, val_f1, val_cm = evaluate(model, val_loader, cost_matrix)
        model.train()

        # adding checkpointing (similar to miniproject 3)
        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(model.state_dict(), 'best_model_C3.pt')

    # load the best model that was saved
    model.load_state_dict(torch.load('best_model_C3.pt'))

