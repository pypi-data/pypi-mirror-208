# Set the RGB values for off (O) and on (X).
O = [0, 0, 0]
X  = [255, 255, 255]

# Define the matrix for each side of the dice.
_matrix = {
  1: [
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, O, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
  2: [
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
  3: [
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, O, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
  4: [
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
  5: [
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, X, X, O, X, X, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
  6: [
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    X, O, X, X, X, O, X, O,
    X, X, X, X, X, X, X, O,
    O, O, O, O, O, O, O, O,
  ],
}