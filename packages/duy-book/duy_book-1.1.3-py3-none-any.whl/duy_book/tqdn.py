from tqdm.notebook import tqdm
class tqdn():
  def __init__(self, iterable, **args):
    self.tqdm = tqdm(iterable, **args)
  def __iter__(self):
    for item in self.tqdm:
      yield self.tqdm, item
