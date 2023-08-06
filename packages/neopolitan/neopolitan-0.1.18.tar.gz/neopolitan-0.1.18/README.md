# neopolitan
A library for displaying "text" on LED boards

## Description

This is a revamp of [stockticker](https://github.com/alyoshenka/stockticker), which queries real-time stock price data, calculates daily fluctuations, and displays it on an LED board. While the end result of that project was cool, this project aims to clarify much of the data display code and make it usable to display any inputted message. See this [sub-readme](https://github.com/alyoshenka/neopolitan/tree/main/src/writing#readme) for an introduction to how data can be used to make the board display "human-readable".

Given that access to hardware boards can be constrictive and testing can be difficult, this project aims to support data display on a graphical interface so that anyone can access it. `pygame` is used to display the graphical display, while the `neopixel` (hence the project name) library [will be] is used to interface with the hardware board.

## Installation and Usage
1. Clone the project
1. Navigate to the project folder
1. Install requirements with `pip install -r requirements.txt`
1. Run the `src/main.py` with `Python3`

### Command Line Arguments
`python[3] src/main.py {args}`
- `--message {message_to_display}`/`-m {message_to_display}`
  - Displays the given message on the board (enclose in quotes if multiple words)
- `--graphical {True/False}`/`-g {True/False}`
  - Switches between the graphical output and hardware board output **not yet functional**
- `--scroll-speed {slow/medium/fast}`/`-s {slow/medium/fast}`
  - Controls how quickly the display scrolls across the screen
- `--wrap {True/False}`/`-w {True/False}`
  - Determines whether the display should "wrap around" when it gets to the end, or just show a blank screen

todo: command line examples (w/ vids?)
