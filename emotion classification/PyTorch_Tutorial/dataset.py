import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader


class RandomDataset(Dataset):
    def __init__(self):
        self.x = torch.randn((128, 64))
        self.y = torch.randn((128, 1))

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

    def __len__(self):
        return self.x.shape[0]


if __name__ == '__main__':
    dataset = RandomDataset()
    train_loader = DataLoader(dataset=dataset, batch_size=32, shuffle=True)
    for epoch in range(100):
        for i, (x, y) in enumerate(train_loader):
            print(i)
