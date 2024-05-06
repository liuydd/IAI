import torch
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, sentence, label):
        self.sentence = torch.tensor(sentence, dtype=torch.float)
        self.label = torch.tensor(label, dtype=torch.float)
    
    def __len__(self):
        return len(self.sentence)
    
    def __getitem__(self, idx):
        word = self.sentence[idx]
        label = self.label[idx].long()
        return word, label