# Import the class.
from ffdice import Dice

# Define colors.
colors = ("black", "white", "purple", "blue", "green", "yellow", "orange", "red")

# Create a dice with as much sides as there are colors.
dice = Dice(len(colors))

# Use the output of the `roll()` method to pick the appropriate color.
index = dice.roll()
color = colors[index - 1]
print("You rolled %s!" % color)
