import unittest
from ffdice import Dice

class TestDice(unittest.TestCase):
  
  # Basic test (D6).
  # ---
  # Roll a couple of times to determine the highest outcome. 
  # For a basic dice, obviously, this can't be higher than 6.
  def test_default(self) -> None:
    dice = Dice()
    outcomes = []
    # The probability of rolling a 6 is almost 100% when rolling 50 times.
    # Reference: https://www.gigacalculator.com/calculators/dice-probability-calculator.php
    for i in range(50):
      outcomes.append(dice.roll())
    self.assertEqual(max(outcomes), 6, "The expected output should be equal to 6.")

  # Unique outcomes.
  # ---
  # Pass `True` as an argument to the `roll()` method.
  # By doing so, no outcome should match its predecessor.
  def test_unique(self) -> None:
    dice = Dice()
    outcomes = []
    duplicate = False
    for i in range(50):
      rng = dice.roll(True)
      if len(outcomes) > 0 and rng == outcomes[-1]:
        duplicate = True
        break
      else:
        outcomes.append(rng)
    self.assertEqual(duplicate, False, "The value of variable `duplicate` should remain `False`.")
  
  # Single sided dice (D1).
  # ---
  # When passing a list with a single value, the only possible outcome is 1.
  def test_single_sided(self) -> None:
    dice = Dice(1)
    self.assertEqual(dice.roll(), 1, "The expected output should be equal to 1.")
  
  # Twenty sided dice (D20).
  # ---
  # When passing a list with a single value, the only possible outcome is 1.
  def test_twenty_sided(self) -> None:
    dice = Dice(20)
    outcomes = []
    # The probability of rolling a 20 is almost 100% when rolling 100 times.
    # Reference: https://www.gigacalculator.com/calculators/dice-probability-calculator.php
    for i in range(100):
      outcomes.append(dice.roll())
    self.assertEqual(max(outcomes), 20, "The expected output should be equal to 20.")

if __name__ == '__main__':
  unittest.main()