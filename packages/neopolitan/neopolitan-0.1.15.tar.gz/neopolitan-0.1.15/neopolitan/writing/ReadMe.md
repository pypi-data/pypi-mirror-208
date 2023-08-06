# Data Transformation

This document explains how the letters for the LED board are defined, and how that data is transormed to be usable by the board and graphical displays.

### How does the board work? How are letters defined?
The board is made of a contiguous (single line) of LEDs.

To draw letters in a matrix, the assumption would be that they could be accessed with indices as such:

|    |    |   |   |   |
|--- |--- |---|---|---|
| 0  | 8  | 16 | 24 | 32 |
| 1  | 9  | 17 | 25 | 33 |
| 2  | 10 | 18 | 26 | 34 |
| 3  | 11 | 19 | 27 | 35 |
| 4  | 12 | 20 | 28 | 36 |
| 5  | 13 | 21 | 29 | 37 |
| 6  | 14 | 22 | 30 | 38 |
| 7  | 15 | 23 | 31 | 39 |

So to draw an "a", you could define as follows (where a * represents a color, and a blank entry represents "off"):

|    |    |   |   |   |
|--- |--- |---|---|---|
|   |   |   |   |  |
|   |   |   |   |  |
|   | * | * |   |  |
|   |   |   | * |  |
|   | * | * | * |  |
| * |   |   | * |  |
|   | * | * | * |  |
|   |   |   |   |  |

Thus `a = [[5], [10, 12, 14], [18, 20, 22], [27, 28, 29, 30]]`

*(This is also just how the symbols were defined initially, and changing the code is tedious and time-consuming.)*

This is how the symbols in `letters_*.py` are defined.

However, due to the layout of the board, the indices are "snaked" up and down, so that that the layout of the board looks like this:

```
   _   _   
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
|_| |_| |_
```
So the actual LED indices look like this:

|    |    |   |   |   |
|--- |--- |---|---|---|
| 0  | 15 | 16 | 31 | 32 |
| 1  | 14 | 17 | 30 | 33 |
| 2  | 13 | 18 | 29 | 34 |
| 3  | 12 | 19 | 28 | 35 |
| 4  | 11 | 20 | 27 | 36 |
| 5  | 10 | 21 | 26 | 37 |
| 6  | 9  | 22 | 25 | 38 |
| 7  | 8  | 23 | 24 | 39 |

The data can be used as if the board layout was the intuitive one, so long as every other "column" is "flipped" when drawing.

Letters are defined in this "grid" fashion because it is easier to understand. 

Data is stored in the array fashion because this is what the board uses

### How does a letter go from "grid" form to "array" form?

see `data_transformation.py`
1. For any symbol `sym`:
    1. Create a `frame` array to hold the created `height=1` array. Initialize all it's values to `None`.
    1. For every `row` in every `column` of `sym`:
        1. Set `frame[val]` to be a valid `color`
    1. Return `frame`



