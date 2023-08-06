"""
Input tools, currently supported getting a bounded integer and a two-dimensional array.
"""

from typing import Any

def bounded_int(lower: int, upper: int, prompt: str = None, 
                type_error: str = "You must enter an integer: ", 
                bounds_error: str = None) -> int:
    """
    Forces the user to return an integer between the two entered values.

    Arguments: A lower and an upper bound for the integers. An optional prompt.

    Raises: An AssertionError if the types of each the lower and upper bound are not integers, or is the upper bound si not greater than the lower

    Returns: The correct integer that the user inputs.
    """

    assert isinstance(lower, int), f"Lower bound must be an integer, not '{type(lower)}'."
    assert isinstance(upper, int), f"Upper bound must be an integer, not '{type(upper)}'."
    assert upper > lower, "Upper bound must be greater than lower bound."

    if not prompt:
        prompt = f"Please enter a number between {lower} and {upper}: "

    if not bounds_error:
        bounds_error = f"The number must be between {lower} and {upper}: "

    user_input = (lower - 1) / 1    # convert to float
    flag_type_error = False
    while not (lower <= user_input <= upper):
        try:
            if isinstance(user_input, float):       # get first input
                user_input = int(input(prompt))
            elif flag_type_error:
                user_input = int(input(type_error))     
                flag_type_error = False
            else:
                user_input = int(input(bounds_error))
        except:
            user_input = lower - 1      # reset to a set out of bounds value
            flag_type_error = True

    return user_input

def two_dim_array(rows: int, cols: int = None, delimiter: str = " ", item_type: int = str) -> list[list[Any]]:

    """
    Arguments: A number of rows, a number of columns, and an optional delimiter. The delimiter is set to spaces by default. To split strings into individual characters, enter a delimiter of ''. 
    You can also enter a type (str, float) in which the items will be read. The default is str.

    Raises: An AssertionError for invalid row or column counts.
    
    Returns: A 2-d list will be in the form of list[rows][cols].
    """

    output = []
    for _ in range(rows):
        row = input()           # delimiter for rows must be a \n character
        if delimiter == "":
            items = list(row)   # splits string into char array
        else:
            items = [item for item in row.split(delimiter) if item != '']    # otherwise split by the delimiter  
        assert cols == None or (cols != None and len(items) == cols), "Column count parameter and items in the row do not match."
        output.append(list(map(item_type, items)))

    return output