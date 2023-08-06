# How Operations Work

## When the board display is running, how do we send it state updates?

### What Things Do We Need to Update?
- operation: What functionality the board is performing (simple messages, animations, etc)
    - messages: Display text across the board
        - message text: What words (and symbols) are displaying
        - scroll speed: How fast the message is moving across the screen, if at all. Can be specified by an enum ('slow', 'medium', 'fast') or a "scroll wait": how much time to sleep before moving over one "row"
        - scroll wrap: Whether the message wraps over once it finishes displaying, or just waits with an empty display
        - ~~display medium: Switch between the graphical or hardware output, where applicable~~ (done automatically based on OS)
    - animations: todo
- Control Signals:
    - open: Initialize the display
    - close: Deinitialize the display

### How Do We Do This?
todo: make better then update doc

When the `main` function is run, there is an optional `events` parameter that excepts a `Queue` object. On every loop, this queue is checked for new events:
#### How Events Are Processed
An event is passed as a simple string. For example, 'say hello' or 'exit'.
todo: should be more advanced. 
This string is split by spaces and then parsed:
##### How Event Strings are Parsed
- first word:
    - 'exit': close the board and quit the application
    - 'say': set the message of the board
        - following arguments: join them into one space-separated string (yes, they were split then joined again, it's a WIP) and set this as the message currently displaying on the board
    - 'speed': set the scroll speed of the board based on the second argument
        - 'slow'/'medium'/'fast': set the scroll speed to a predefined value for this enumerator
        - float: set the scroll wait (how long the program sleeps before "moving over" one "column") to this value, in seconds
    - 'wrap': set whether the board wraps when it reaches the end of its display data
        - 'True'/1
        - 'False'/0