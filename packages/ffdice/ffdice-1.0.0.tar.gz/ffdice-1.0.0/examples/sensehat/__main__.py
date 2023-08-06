# Import the class and required modules.
from ffdice import Dice
from matrix import _matrix
from sense_hat import SenseHat # type: ignore
from time import sleep
import atexit

# Create necessary instances and variables, the purpose of which will be explained below.
dice = Dice()
hat = SenseHat()
degrees = (0, 90, 180, 270)
rolls = 15
threshold = 2

# Method to clear the SenseHat LED display.
def reset() -> None:
  hat.clear()

# Execute the reset method when exiting the program.
atexit.register(reset)

# Main functionality.
while True:
  # Determine the acceleration of the SenseHat while shaking.
  acceleration = hat.get_accelerometer_raw()
  x = abs(acceleration['x'])
  y = abs(acceleration['y'])
  z = abs(acceleration['z'])
  # Continue if the acceleration exceeds the `threshold` value defined above.
  if (x > threshold or y > threshold or z > threshold):
    # Use the value of `rolls` to call the `roll()` method multiple times in a row.
    # Set its argument `animate` to `True` in order to prevent the same number from being generated twice in a row.
    # This creates a simulation of a single dice roll.
    i = 0
    while (i < rolls):
      # Use the outcome of the `roll()` method to retrieve the appropriate matrix image, and display it on the LED display.
      number = dice.roll(True)
      image = _matrix[number]
      hat.set_pixels(image)
      # Cycle through the different degree values.
      # Rotate the LED display to create the illusion of a dice roll.
      rotation = degrees[i % len(degrees)]
      hat.set_rotation(rotation, False)
      # Continue loop.
      i += 1
      sleep(0.1)
