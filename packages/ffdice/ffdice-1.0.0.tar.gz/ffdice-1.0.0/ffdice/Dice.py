# ---
# Dice
# ---
# An RNG subclass that acts as a basic dice.
# It may return a random number between 1 and 6, based on its sides.
from .RNG import RNG

class Dice(RNG):

  #region Attributes

  __sides: int

  #endregion

  #region Public methods

  # Roll the dice.
  # ---
  # Picks a random side of the dice each time.
  # By setting the `unique` argument to `True`, the roll is simulated in the sense that the dice can't show the same number twice in a row.
  # (If it could, it wouldn't be rolling.)
  # ---
  # @param unique (bool)    Determines whether the previous outcome should be excluded.
  # ---
  # @returns rng (int)      Randomly generated number
  def roll(self, unique: bool = False) -> int:
    return super().generate(unique)

  #endregion

  #region Instance special methods

  # Construct.
  # ---
  # Called after the instance is created by `__new__()`.
  # ---
  # @param sides (int)    Amount of sides of the dice.
  def __init__(self, sides: int = 6) -> None:
    if sides != None:
      self.__sides = sides
    super().__init__(self.__sides)

  #endregion
