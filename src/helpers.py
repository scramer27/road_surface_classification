import torch
import numpy as np

# generic evaluation metric helpers
def confusion_matrix(y_pred, y_true):
    # counts [0,0] is TN, [0, 1] is FP, [1,0] is FN, [1,1] is TP
    counts = torch.zeros((2, 2), dtype=torch.float32).to(y_pred.device)
    for i in range(2):
        for j in range(2):
            counts[i, j] = ((y_pred == j) & (y_true == i)).sum()
    return counts

def expected_cost(confusion_matrix, cost_matrix):
    m = confusion_matrix.sum().item()
    return (confusion_matrix * cost_matrix.to(confusion_matrix.device)).sum().item() / m

def accuracy(y_pred, y_true):
    return (y_pred == y_true).float().mean().item()

def precision(confusion_matrix):
    return confusion_matrix[1, 1] / (confusion_matrix[0, 1] + confusion_matrix[1, 1] + 1e-8)

def recall(confusion_matrix):
    return confusion_matrix[1, 1] / (confusion_matrix[1, 0] + confusion_matrix[1, 1] + 1e-8)

def f1_score(precision, recall):
    return 2 * (precision * recall) / (precision + recall + 1e-8)

# logistic regression + 1D CNN helpers
def costs_and_accuracies(q_val, y_val, C, T): # adapted from lecture 8
    costs = []
    accuracies = []
    for t in T:
        y_pred = (q_val >= t).int()

        cm = confusion_matrix(y_pred, y_val)
        c = expected_cost(cm, C)
        acc = (cm[0, 0] + cm[1, 1]) / cm.sum()
        accuracies.append(acc.item())
        costs.append(c)
    return costs, accuracies

def binary_cross_entropy(q, y): # adapted from lecture 6
    return -(y * torch.log(q + 1e-8) + (1 - y) * torch.log(1 - q + 1e-8)).mean()

def engineer_features(samples):
    # use summary statistics for each column, rather than using entire data window
    features = []
    for col in range(samples.shape[1]):
        features.append(samples[:, col].mean())
        features.append(samples[:, col].std())
        features.append(samples[:, col].max())
        features.append(samples[:, col].min())
    return features

def flatten_window(samples):
    return samples.reshape(-1)

# helper for 1D CNN
def evaluate(model, loader, cost_matrix):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for X_batch, y_batch in loader:
            preds = (model(X_batch) >= 0.5).float()
            all_preds.append(preds.reshape(-1))
            all_labels.append(y_batch.reshape(-1))

    y_pred = torch.cat(all_preds)
    y_true = torch.cat(all_labels)

    cm  = confusion_matrix(y_pred, y_true)
    acc = accuracy(y_pred, y_true)
    ec  = expected_cost(cm, cost_matrix)
    p   = precision(cm)
    r   = recall(cm)
    f1  = f1_score(p, r)
    return acc, ec, f1, cm
