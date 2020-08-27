"""Utility functions that are used throughout the codebase."""


def format_string(s):
    """Formats the input depending on if it is a string or a list of strings.

    Determines the type of the input. If it is a string then strips leading spaces and lowercases all letters. If it is a list, then the aforementioned process is applied to each of the list elements. 

    Arg: 
        s: string or list of strings that needs to be formatted

    Return: 
        a formated string is returned if a string is provided
    a formated list is returned if a list is provided
    """
    if isinstance(s, str):
        return s.strip().lower()
    if isinstance(s, list):
        res = []
        for string in s:
            if isinstance(string, str):
                res.append(string.strip().lower())
            else:
                try:
                    res.append(str(string).strip().lower())
                except:
                    res.append(
                        string
                    )  # NOTE when the element is not of string typ (we can handle this case different if necessary)
        return res
    return s  # NOTE Simply returns the input if the input is not a string or a list

    #  TestCases:
    #     print(format_string("  JaS on   "))
    #     print(format_string(["  JaS on   C  ", "CHE"]))
    #     print(format_string(["  JaS on   C  ", "CHE", 6]))
    #     print(format_string(6))
    #     print(format_string({"TeamRU": 2020}))

