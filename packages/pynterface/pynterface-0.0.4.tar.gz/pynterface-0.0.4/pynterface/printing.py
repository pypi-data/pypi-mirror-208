"""
This part of the module includes useful tools for printing. Currently, the following are supported:
- Clear screen
- Clear screen than print message
- 'Smooth' print a message
- Center text
- Apply a gradient to text or background
"""

import os
import re
from typing import Any, Iterable
from time import sleep
from .style import Color, Background 

# \033[ followed by a combo of numbers and ; ended with a single letter
__ANSI_PATTERN = "\033\[[0-9|;]*[a-z|A-Z]"
__CENTERED_FORBIDDEN_CHARS = "[\t]"
__UNIQUE_CHAR_LENGTHS = {
    "\b": -1
}

def clear_window() -> None:
    """
    Clears the terminal window.
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def clear_print(message: Any, end: str = "\n") -> None:
    """
    Clears the terminal window and prints the prompt.
    """
    clear_window()
    print(message, end=end)

def smooth_print(message: Any, delay: int = 25, end: str = "\n") -> None:
    """
    Prints a message, smoothly.

    Arguments: A message, and delay (in milliseconds), and an optional end. 
    """

    # splits into ascii
    chars = __split_esc_chars(str(message))

    # prints each character with a delay
    for char in chars:
        if re.search(__ANSI_PATTERN, message) == None:    # delay only if ansi
            sleep(delay/1000)       
        print(char, end="")
        
    # prints the end (optional)
    print(end, end="")

def centered(message: str | Iterable[str], margin: int = 2) -> str:
    """
    Centers several lines of text.
    """
    
    assert isinstance(message, (str, Iterable)), "Messages must be iterable."
    assert isinstance(margin, int), "Margin must be an integer."

    # splits depending on the types
    if isinstance(message, str): msgs = message.split("\n")
    else: msgs = [*message]

    # preprocessing to split newlines into two and remove forbidden characters
    for i in range(len(msgs)-1, -1, -1):
        line = re.sub(__CENTERED_FORBIDDEN_CHARS, '', msgs[i])  # remove forbidden characters and strip whitespace
        if "\n" in line:
            msgs = msgs[0:i] + line.split('\n') + msgs[i+1:]
        else:
            msgs[i] = line  # different kinds of line replacement

    msgs = [__split_esc_chars(line.strip()) for line in msgs]

    # calculate the lengths of each segment
    lens = [sum([__get_effective_len(c) for c in line]) for line in msgs]
    max_len = max(lens)

    output = ""

    # adds lines and adds whitespace
    for line, ln in zip(msgs, lens):
        output += (margin + (max_len-ln)//2) * " " + "".join(line) + (margin + (max_len-ln) - (max_len-ln)//2) * " " + "\n"

    return output[:-1:] # remove last \n

def __get_effective_len(char: str) -> int:
    """
    Gets the effective length of a character for things like centering the text.
    """

    if re.match(__ANSI_PATTERN, char):
        return 0
    elif char in __UNIQUE_CHAR_LENGTHS:
        return __UNIQUE_CHAR_LENGTHS[char]
    else:
        return len(char)

def __split_esc_chars(message: str) -> list[str]:
    """
    Splits a message up into characters and escape codes.
    """

    """
    Note: "between" represents characters that are between the ANSI codes.
    """

    char_list = []

    # get codes and normal things in between
    ansi_codes = re.finditer(__ANSI_PATTERN, message)
    matches = [(match.start(), match.end(), match.group()) for match in ansi_codes]

    i = 0
    while i < len(message):

        # check if start is an ansi value
        if len(matches) > 0 and i == matches[0][0]:
            char_list.append(matches[0][2])     # add match
            i = matches[0][1]                   # move index to end of match
            matches.pop(0)                      # get rid of it
        else:
            char_list.append(message[i])        # otherwise add normal char
            i += 1
        
    return char_list

def gradient(message: str, left_rgb: tuple[int, int, int], right_rgb: tuple[int, int, int], mode: str = "background") -> str:
    """
    Returns a string with the gradient applied.
    """

    assert all([0 <= color <= 255 for color in left_rgb+right_rgb]), "Invalid RGB number entered."
    assert len(left_rgb) == len(right_rgb) == 3, "Tuple with RGB values must have a length of 3." 
    assert isinstance(message, (str, Iterable)), "Message must be a string or a list of strings representing newlines."
    assert mode in ["text", "background"], "Invalid mode."

    # tune hte rgb value depending on progress in the line: a and b are start and end values, i is the progress, and n is the max count.
    def get_value(a, b, i, n): return a + round((b-a)*(i/n))  

    # filter mode
    if mode == "text": method = Color
    elif mode == "background": method = Background
    
    # splits depending on the types
    if isinstance(message, str): messages = message.split("\n")
    else: messages = [*message]

    messages = [__split_esc_chars(line) for line in messages]
    max_len = max([len(s) for s in messages]) - 1
    rgb_vals = [tuple([get_value(left_rgb[ii], right_rgb[ii], i, max_len) for ii in range(3)]) for i in range(max_len+1)]
    output = f"{method.RESET_COLOR if method == Color else method.RESET_BACKGROUND}\n".join(            # joins the lines by a reset color/background
        ["".join([method.RGB(rgb_vals[i]) + line[i] for i in range(len(line))]) for line in messages]   # creates the line
    )

    return output