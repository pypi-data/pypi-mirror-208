# -----------------------
# Random number generator
# -----------------------
# Class that generates a random number between 1 and a given maximum value.
from random import randint

class RNG:

  #region Attributes

  __list: list
  __prev_rng: int

  #endregion

  #region Public methods

  # Generate random number.
  # ---
  # Picks a random number from the list.
  # ---
  # @param unique (bool)  Determines whether the previously generated number should should be excluded as a possible outcome.
  # ---
  # @returns rng (int)          Randomly generated number
  def generate(self, unique: bool = False) -> int:
    match = 0 if unique == False else self.__prev_rng
    filtered = list(filter(lambda x: x != match, self.__list))
    index = randint(1, len(filtered))
    rng = filtered[index - 1]
    self.__prev_rng = rng
    return rng

  #endregion

  #region Instance special methods

  # Construct.
  # ---
  # Called after the instance is created by `__new__()`.
  # ---
  # @param maximum (int)  The maximum value of the range.
  def __init__(self, maximum) -> None:
    try:
      self.__list = []
      self.__prev_rng = 0
      for i in range(0, maximum):
        self.__list.append(i + 1)
    except Exception as err:
        print(err)

  def __call__(self, *args):
    return self.__init__(args)

  #endregion
