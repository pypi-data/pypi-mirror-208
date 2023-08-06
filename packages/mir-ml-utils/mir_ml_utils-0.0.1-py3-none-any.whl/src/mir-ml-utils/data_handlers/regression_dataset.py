from typing import List, Any, Callable
import torch
import torch.utils.data as data


class Regression1DDataset(data.Dataset):

    def __init__(self, X, y, data_transform: Callable = None,
                 label_transform: Callable = None):
        super(Regression1DDataset, self).__init__()
        self.X = X.reshape(-1, 1)
        self.y = y.reshape(-1, 1)
        self.data_transform = data_transform
        self.label_transform = label_transform

    def __getitem__(self, index: int) -> tuple:
        return torch.tensor(self.X[index, :], dtype=torch.float32), \
               torch.tensor(self.y[index], dtype=torch.float32)

    def __len__(self) -> int:
        return self.X.shape[0]