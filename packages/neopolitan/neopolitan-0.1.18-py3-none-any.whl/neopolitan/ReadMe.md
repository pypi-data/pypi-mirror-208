# Code Explanation

## ToDo: more stuff here

## Board Runner
### Problem
When the main program runs, it instantiates an LED board and begins drawing animations on it. The issue is that there was originally no way to interrupt this flow of execution with a new board operation. The board can't run with its initial provided state forever because the function of this application is to be able to send new operations for it to display. The question of "How do we do this?" arises.
### Solution
Instead of running the board code directly from the main application, it is run on a thread. This thread is provided a queue as an argument. This queue holds events. On every execution loop, the board code checks for new events in the queue and processes them. The main application can now add events to the queue for the board.
#### Event Organization
Events are organized in a queue and represented as strings. These strings are split by the space character and then processed in order.
- `"exit"`: stop execution of the program
- `"say"`: interrupt execution and display a new message
  - `message`: the new message to display
- `"do"`: perform an operation
  - `operation`: the operation to perform (ex. some type of animation)
### Questions and Considerations
This was a tricky problem to solve, and it seemed like there are multiple ways to go about it. This solution does not feel like the best or most correct way, however it does work and it seems to work well.
- Is this the correct way to do this?
- How do we get information back from the board if there is an error? Is it acceptable for this to be a one-way street given the nature of the project?
### How to Use This Code
todo: document how to utilize this solution to run the board from a different program