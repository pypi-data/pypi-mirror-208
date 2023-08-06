"""
All ANSI codes for colors are adapted from w3schools's ANSI colors reference:
https://www.w3schools.blog/ansi-colors-java

This is my attempt to reproduce colorama's implementation!
Combinations of styles (backgrounds, colors, and text styles) are possible.
This version includes the ability to modify RGB values of colors, set custom colors, and move the cursor.
"""

class Text:

    """
    This class stores information about editing text styles.
    """

    RESET_ALL =     "\033[0m"
    RESET_STYLE =   "\033[22m"

    BOLD =          "\033[1m"
    DIM =           "\033[2m"
    ITALIC =        "\033[3m"
    UNDERLINE =     "\033[4m"
    BLINKING =      "\033[5m"
    INVERTED =      "\033[7m"
    STRIKETHROUGH = "\033[9m"

    HIDE_CURSOR =   "\033[?25l"
    SHOW_CURSOR =   "\033[?25h"

    def MOVE_CURSOR_UP(lines: int = 1):
        """
        Returns an ANSI code to move the cursor up by <lines> lines.
        Through testing, I find that this seems to clear the lines that you go up from.
        """
        assert isinstance(lines, int) and lines >= 0, "Number of lines to move up must be a nonnegative integer."
        return f"\033[{lines}A"
    
    def MOVE_CURSOR_DOWN(lines: int = 1):
        """
        Returns an ANSI code to move the cursor down by <lines> lines.
        """
        assert isinstance(lines, int) and lines >= 0, "Number of lines to move up must be a nonnegative integer."
        return f"\033[{lines}B"
    
    def MOVE_CURSOR_RIGHT(cols: int = 1):
        """
        Returns an ANSI code to move the cursor right by <cols> columns.
        """
        assert isinstance(cols, int) and cols >= 0, "Number of columns must be a nonnegative integer."
        return f"\033[{cols}C"
    
    def MOVE_CURSOR_LEFT(cols: int = 1):
        """
        Returns an ANSI code to move the cursor left by <cols> columns.
        """
        assert isinstance(cols, int) and cols >= 0, "Number of columns must be a nonnegative integer."
        return f"\033[{cols}D"

class Background:

    """
    This class stores information about modifying the background color.
    """

    RESET_BACKGROUND =  "\033[49m"
    RESET_ALL =         "\033[0m"

    BLACK =     "\033[40m"
    RED =       "\033[41m"
    GREEN =     "\033[42m"
    YELLOW =    "\033[43m"
    BLUE =      "\033[44m"
    PURPLE =    "\033[45m"
    CYAN =      "\033[46m"
    WHITE =     "\033[47m"

    BLACK_BRIGHT =     "\033[100m"
    RED_BRIGHT =       "\033[101m"
    GREEN_BRIGHT =     "\033[102m"
    YELLOW_BRIGHT =    "\033[103m"
    BLUE_BRIGHT =      "\033[104m"
    PURPLE_BRIGHT =    "\033[105m"
    CYAN_BRIGHT =      "\033[106m"
    WHITE_BRIGHT =     "\033[107m"

    def RGB(rgb: tuple[int, int, int]) -> str:

        """
        Returns the ANSI escape code for a background color in RGB.
        """

        for var in rgb:
            assert isinstance (var, int) and 0 <= var <= 256, "Invalid RGB value!"
        return f"\033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    
    def SET(name: str, rgb: tuple[int, int, int]) -> None:

        """
        Sets a custom background color given its name and a tuple containing (r, g, b) values.
        Call this color using: Background.NAME, where NAME is the entered name.
        """

        assert isinstance(name, str), "Name must be a string!"
        setattr(Background, name, Background.RGB(rgb))

class Color:

    """
    This class stores information about modifying the foreground color (color of text)
    """

    RESET_COLOR =   "\033[39m"
    RESET_ALL =     "\033[0m"

    BLACK =     "\033[30m"
    RED =       "\033[31m"
    GREEN =     "\033[32m"
    YELLOW =    "\033[33m"
    BLUE =      "\033[34m"
    PURPLE =    "\033[35m"
    CYAN =      "\033[36m"
    WHITE =     "\033[37m"

    BLACK_BRIGHT =     "\033[90m"
    RED_BRIGHT =       "\033[91m"
    GREEN_BRIGHT =     "\033[92m"
    YELLOW_BRIGHT =    "\033[93m"
    BLUE_BRIGHT =      "\033[94m"
    PURPLE_BRIGHT =    "\033[95m"
    CYAN_BRIGHT =      "\033[96m"
    WHITE_BRIGHT =     "\033[97m"

    def RGB(rgb: tuple[int, int, int]) -> str:

        """
        Returns the ANSI escape code for a text color in RGB.
        """

        for var in rgb:
            assert isinstance(var, int) and 0 <= var <= 256, "Invalid RGB value!"
        return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    
    def SET(name: str, rgb: tuple[int, int, int]) -> None:

        """
        Sets a custom text color given its name and a tuple containing (r, g, b) values.
        Call this color using: Color.NAME, where NAME is the entered name.
        """

        assert isinstance(name, str), "Name must be a string!"
        setattr(Color, name, Color.RGB(rgb))

def demo():

    """
    A simple demonstration of the different colors supported.
    """

    # prints examples for each property of the color classes
    def printing_loop(var):
        for name in dir(var):
            if name[0] != "_" and sum([kw in name for kw in ["RESET", "RGB", "SET", "CURSOR"]]) == 0:
                modifier = getattr(var, name)
                print(f"{modifier}{var.__name__}.{name}{var.RESET_ALL}")

    # test cases for normal color properties
    print(f"{Text.BOLD}Colors:{Text.RESET_STYLE}")
    printing_loop(Color)
    print(f"{Text.BOLD}Backgrounds:{Text.RESET_STYLE}")
    printing_loop(Background)
    print(f"{Text.BOLD}Text Styles:{Text.RESET_STYLE}")
    printing_loop(Text)

    # test cases for rgb colors
    print(f"{Color.RGB((100, 200, 150))}Color.RGB((100, 150, 200)){Text.RESET_ALL}")
    print(f"{Background.RGB((200, 100, 100))}Background.RGB((200, 100, 100)){Text.RESET_ALL}")

    # test cases for setting values
    Color.SET("COOL_BLUE", (100, 150, 200))
    print(f"{Color.COOL_BLUE}Color.SET(\"COOL_BLUE\", (100, 150, 200)); Color.COOL_BLUE")

if __name__ == "__main__":
    demo()