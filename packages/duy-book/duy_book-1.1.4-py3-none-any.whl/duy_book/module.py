import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.optim.lr_scheduler as sched
from torchsummary import summary
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
from .colab import ColabOutput
from .tqdn import tqdn

class Module(nn.Module):
  def forward(self, input):
    return self.module.forward(input)
  
  def init(self, optimizer=optim.Adam, lr=1e-3, scheduler=sched.CosineAnnealingLR, T_max=100):
    self.cuda()
    self.optimizer = optimizer(self.parameters(), lr)
    self.scheduler = scheduler(self.optimizer, T_max)
    return self
  
  def summary(self, input_size, batch_size=-1):
    for param in self.parameters():
      device = str(param.device).split(':')[0]
      return summary(self, input_size, batch_size, device)
  
  def test(self, loader):
    self.eval()
    accuracy = 0
    with torch.no_grad():
      for bar, (images, labels) in tqdn(loader, desc='Testing\t'):
        predict = self(images).argmax(1)
        accuracy += (predict == labels).sum().item()
        bar.set_postfix_str('Accuracy is {:%}'.format(accuracy / len(loader.dataset)))
  
  def fit(self, epochs:int, loaders:list, losser=F.cross_entropy):
    colab = ColabOutput()
    losses = [[], [], []]
    for bar, epoch in tqdn(range(epochs), desc='Training'):
      for param_group in self.optimizer.param_groups:
        bar.set_postfix_str(f'lr:{param_group["lr"]}')
        break

      self.train()
      for images, labels in loaders[0]:
        self.optimizer.zero_grad()
        loss = losser(self(images), labels)
        loss.backward(), self.optimizer.step()
        losses[0].append(loss.item())
      self.scheduler.step()
      losses[0][epoch] = sum(losses[0][epoch:]) / len(loaders[0])

      if len(loaders) == 2:
        with torch.no_grad():
          self.eval()
          for images, labels in loaders[1]:
            output = self(images)
            losses[1].append(losser(output, labels).item())
            losses[2].append((output.argmax(1) == labels).sum().item())
          losses[1][epoch] = sum(losses[1][epoch:]) / len(loaders[1])
          losses[2][epoch] = sum(losses[2][epoch:]) / len(loaders[1].dataset)

      for i in range(len(losses)): losses[i] = losses[i][:epoch+1]
      with colab:
        plt.plot(losses[0], label='Training')
        plt.plot(losses[1], label='Validation')
        plt.plot(losses[2], label='Accuracy')
        plt.legend()
    return self
