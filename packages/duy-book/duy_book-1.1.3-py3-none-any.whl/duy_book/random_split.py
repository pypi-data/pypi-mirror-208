import torch
def random_split(dataset, lengths):
  lengths[-1] += len(dataset) - sum(lengths)
  return torch.utils.data.random_split(dataset, lengths)
