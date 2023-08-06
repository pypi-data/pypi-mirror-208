"""
This part of the module holds programs that helps getting user input through menus.
"""

from typing import Iterable, Any
from .input import bounded_int

def __map_to_str(opt):

    """
    Turns the variable into a string.
    """

    if isinstance(opt, (bool, str, float, int, object)):
        return str(opt)
    try:
        return opt.__name__
    except:
        raise AssertionError("Option type unable to be converted to string using __name__.")

def __list_print(prompt: str, spacing: int, str_options: list) -> None:
    """
    Prints menu options and beginning prompt.
    """

    if prompt:
        print(prompt)

    for index, opt in enumerate(str_options):
        print(f"{' '*spacing}{index+1}. {opt}")

def numbered_menu(options: Iterable[Any], beginning_prompt: str = None, 
                  selection_prompt: str = None, spacing: int = 4, return_number: bool = False) -> Any:

    """
    Creates a numbered menu, in the following format:
    ```
    '''
    <prompt>
        1. Option
        2. Option
        3. Option
    Please enter a number between {lower} and {upper}:
    '''
    ```
    Arguments: The list of options to enter, which can include things like classes, functions, or simple datatypes. An optional prompt, and an optional spacing value (how many spaces the options are intended by). Additionally, you can enter a return_number parameter in order to return the number rather than its associated value.

    Raises: An AssertionError for incompatible types.

    Returns: The choice selected by the user.
    """

    assert isinstance(options, Iterable), "Options must be iterable!"
    assert len(options) >= 2, "There should be at least two values to select from!"
    assert isinstance(spacing, int) and spacing >= 0, "Spacing must be a non-negative integer!"

    str_options = list(map(__map_to_str, options))

    __list_print(prompt=beginning_prompt, spacing=spacing, str_options=str_options)
    
    choice = bounded_int(1, len(str_options), prompt=selection_prompt)

    if return_number:
        return choice
    
    return options[choice - 1]

def list_menu(options: Iterable[Any], beginning_prompt: str = None, 
              selection_prompt: str = "Enter your choice: ",
              error_prompt: str = "Invalid choice, enter a valid one: ",
              spacing: int = 4, selector: str = '-') -> Any:

    """
    Creates a numbered menu, in the following format:
    ```
    '''
    <prompt>
        - Option
        - Option
        - Option
    Please enter yor option:
    '''
    ```
    Arguments: The list of options to enter, which can include things like classes, functions, or simple datatypes. An optional prompt, and an optional spacing value (how many spaces the options are intended by).

    Raises: An AssertionError for incompatible types.

    Returns: The choice selected by the user.
    """
    
    assert isinstance(options, Iterable), "Options must be iterable!"
    assert len(options) >= 2, "There should be at least two values to select from!"
    assert isinstance(spacing, int) and spacing >= 0, "Spacing must be a non-negative integer!"
    assert isinstance(selector, str), "List element introducer must be a string!"

    str_options = list(map(__map_to_str, options))

    __list_print(prompt=beginning_prompt, spacing=spacing, str_options=str_options)

    choice = input(selection_prompt)

    while choice.strip() not in str_options:
        choice = input(error_prompt)

    return options[str_options.index(choice)]