"""
Supports loading animations, inspired by Auto-GPT's spinner class, found here: https://github.com/Significant-Gravitas/Auto-GPT/blob/master/autogpt/spinner.py
This version supports customizable cycling as well as default classes for quick access. You can also print messages above the spinner.
"""
from __future__ import annotations
from threading import Thread
from time import sleep
from sys import stdout

class Loader():
    
    def __init__(self, message: str, cycle: list[str], delay: int, hide_cursor: bool = True) -> None:

        """
        Creates a new Loader with a message which appears on the same line as the cycler.

        :param str message: The message being printed on the same line as the cycler.
        :param list[str] cycle: The list of strings to cycle between to display loading.
        :param int delay: The number of milliseconds between each item in the cycle.
        :param bool hide_cursor: Whether or not the cursor is hidden while the Loader runs.

        :raises AssertionError: if either the message or the items in the cycle are not strings.

        :return: None
        :rtype: NoneType
        """

        assert all([isinstance(part, str) for part in cycle]), "Cycle must consist of strings only."
        assert isinstance(message, str), "Message must be a string."

        self.max_len = max([len(item) for item in cycle])

        # stores customization values
        self.cycle = cycle
        self.message = message
        self.delay = delay / 1000
        self.hide_cursor = hide_cursor

        # temporary null value 
        self.runner = None

        # stores values for going back and clearing
        self.prev_length = len(self.cycle[0]) 
        
        # for cycling
        self.mod = len(cycle)
        self.index = 0

        # for states
        self.over = False
        self.paused = False
        
        if self.hide_cursor:
            print("\033[?25l", end="")

    @property
    def __state(self):
        """
        Adjusts the index and returns it.
        """
        self.index += 1
        self.index %= self.mod
        return self.index

    def __run(self) -> None:
        """
        Thread that runs the loader.
        """
        try:
            while not self.over:
                if self.paused:
                    continue
                item = self.cycle[self.__state]
                self.__display(item)
                sleep(self.delay)
        finally:
            print("\033[?25h", end="")  # shows cursor no matter what

    def __display(self, item):
        """
        Clears and displays the message.
        """
        self.__clear_animated()
        self.prev_length = len(item)
        print("\r" + self.message + item, end="")
        stdout.flush()

    def __enter__(self) -> Loader:
        self.runner = Thread(target=self.__run)
        self.runner.start()
        return self

    def __exit__(self, _, __, ___):

        # ends and clears
        self.over = True
        self.__clear()

        # print newline
        print(end="\r") 

        # end thread
        self.runner.join()

    def print_above(self, message) -> None:
        """
        Prints the entered string above the Loader.

        :param str message: The message to be printed above the Loader.
        """

        # pause and print message
        self.paused = True
        self.__clear()
        print("\r" + message)
        self.paused = False

        # reset the display
        self.__display(self.cycle[self.__state])
        sleep(self.delay)

    def __clear_animated(self):
        """
        Clears the animated thing.
        """
        print("\b" * self.prev_length 
              + " " * self.prev_length 
              + "\b" * self.prev_length, end="")

    def __clear(self):
        """
        Clears the message.
        """
        print("\r" + " " * (len(self.message) + self.max_len + 1), end="")

class Spinner(Loader):
    """
    A Spinner preset based on the Loader class.
    Cycles between \, |, /, and - to simulate spinning.
    """
    def __init__(self, message: str, delay: int = 50) -> None:
        """
        A Spinner preset based on the Loader class.
        
        :param str message: The message on the same line as the spinner.
        :param int delay: Delay in milliseconds between each item, defaulted to 50.

        :raises AssertionError: if the message is not a string.

        :return: None
        :rtype: NoneType
        """
        super().__init__(message=message, cycle=["/", "-", "\\", "|"], delay=delay, hide_cursor=True)

class Ellipsis(Loader):
    """
    A Ellipsis - "..." - preset based on the Loader class.
    Cycles up to a given number of periods then repeats.
    """
    def __init__(self, message: str, periods: int = 3, delay: int = 200) -> None:
        """
        A Ellipsis - "..." - preset based on the Loader class.
        
        :param str message: The message that will be printed next to the cycler.
        :param int periods: The number of periods at the longest string.
        :param int delay: Delay in milliseconds between each item, defaulted to 200.

        :raises AssertionError: if the message is not a string or if the periods are anything but an int greater than 1.

        :return: None
        :rtype: NoneType
        """
        assert isinstance(periods, int) and periods > 1, "You must have an upper limit of at least 2 periods!"
        super().__init__(message=message, cycle=["."*n for n in range(periods+1)], delay=delay, hide_cursor=True)

def test_loaders():
    """
    Tests the functionality and displays of loaders.
    """
    def __loop():
        """
        Example time-consuming task to test loaders.
        """
        for i in range(1, 100_000_000):
            if i % 40_000_000 == 0:
                yield f"{i:,} is divisble by 40,000,000!"
            elif i % 20_000_000 == 0:
                yield f"{i:,} is almost divisble by 40,000,000!"

    with Loader(message="Loading ", cycle=[str(n) for n in range(10)], delay=10) as loader:
        for output in __loop():
            loader.print_above(output)

    print("Loader done!")

    with Spinner(message="Calculating ") as spinner:
        for output in __loop():
            spinner.print_above(output)

    print("Spinner done!")

    with Ellipsis(message="Periods", periods=15) as ellipsis:
        for output in __loop():
            ellipsis.print_above(output)

    print("Ellipsis done!")

if __name__ == "__main__":
    test_loaders()