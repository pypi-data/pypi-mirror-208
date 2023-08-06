from torch.utils.data import Dataset, DataLoader
class Cudaset(Dataset):
  def __init__(self, dataset: Dataset):
    (X, y) = next(iter(DataLoader(dataset, len(dataset))))
    self.X, self.y = X.cuda(), y.cuda()
  def __len__(self): return len(self.y)
  def __getitem__(self, index): return self.X[index], self.y[index]
