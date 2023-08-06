# Import the class.
from ffdice import Dice

# By omitting parameters in the instance creation, you'll create a dice with 6 sides.
dice_one = Dice()
dice_two = Dice()

# For this instance, the `roll()` method will return a number between 1 and 6.
a = dice_one.roll()
b = dice_two.roll()
print("You rolled %d and %d, adding up to a total of %d!" % (a, b, a + b))
