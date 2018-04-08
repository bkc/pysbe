"exceptions.py - define schema exceptions"

class DuplicateName(ValueError):
    """duplicate name"""
    pass


class DuplicateChoiceValue(ValueError):
    """duplicate Choice Value"""
    pass

class UnknownReference(ValueError):
    """unknown reference"""
    pass
