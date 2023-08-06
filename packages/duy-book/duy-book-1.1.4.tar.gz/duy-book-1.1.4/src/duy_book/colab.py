import IPython, ipywidgets
import matplotlib.pyplot as plt
class ColabOutput(object):
  def __init__(self):
    from google.colab import output
    output.enable_custom_widget_manager()
    self.output = ipywidgets.Output()
    IPython.display.display(self.output)
  def __enter__(self):
    self.output.__enter__()
    IPython.display.clear_output(True)
  def __exit__(self, *args):
    plt.show()
    self.output.__exit__(*args)
