import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset

ACCELS = ['ax', 'ay', 'az', 'atotal']
CLASSES = ['NORMAL', 'POTHOLE']

class LogisticModel: # binary classification (sigmoid)
    def __init__(self, n_features, device):
        self.w = torch.zeros(n_features, 1, requires_grad=True, device=device)

    def forward(self, X): # sigmoid forward function
        return 1 / (1 + torch.exp(-X @ self.w))
    
class RoadSurfaceDataset(Dataset):
    def __init__(self, df, window_length, device, augment=True):
        self.device = device
        self.window_length = window_length
        self.augment = augment
        self.windows = []
        self.labels  = []

        # precompute all windows like birdcall does for spectrograms
        for event, group in df.groupby('event_id'):
            samples = group[ACCELS].values[:window_length]  # (350, 4) or (250, 4) or (150, 4)
            self.windows.append(samples)
            self.labels.append(CLASSES.index(group['label'].iloc[0]))

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, idx):
        # make copies of window
        window = self.windows[idx].copy()

        # create a random time shift
        if self.augment:
            max_shift = self.window_length // 10  # 35 for A, 25 for B, 15 for C
            shift = np.random.randint(-max_shift, max_shift)
            window = np.roll(window, shift, axis = 0)

        # convert to tensor format, placing channels before samples
        x = torch.tensor(window.T, dtype=torch.float32).to(self.device)
        y = torch.tensor(self.labels[idx], dtype=torch.float32).to(self.device)

        return x, y

# CNN class, adapted from lecture
class RoadSurfaceCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.pipeline = nn.Sequential(
            nn.Conv1d(4, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Flatten(),
            nn.LazyLinear(1)
        )

    def forward(self, x):
        return torch.sigmoid(self.pipeline(x))
