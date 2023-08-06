import logging
import json

# Set up basic configuration
logging.basicConfig(
  format='%(asctime)s | %(name)s - %(levelname)s: %(message)s',
  level=logging.INFO,
  filename="pix.log")

# Create a logger
log = logging.getLogger("PIX RUNTIME")


class Data:
  """
  Data class allows you to store and load variables in dictionaries
  """

  def __init__(self, filename):
    self.filename = filename

  def save(self, variables):
    """
    Saves the input {variables} into the designated file.
    """
    with open(self.filename, "w") as f:
      json.dump(variables, f, indent=4)

  def load(self):
    """
    Loads all saved variables from the designated file.
    """
    with open(self.filename, "r") as f:
      variables = json.load(f)
    return variables
