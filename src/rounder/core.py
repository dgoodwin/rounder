""" Core Rounder module. """

class RounderException(Exception):
    """
    Parent of all our custom exceptions.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def array_to_string(array):
    output = ""
    for c in array:
        output = output + str(c) + " "
    return output
