from prettyprinter import cpprint


def dump(*args):
    """Dump variables using prettyprinter"""
    for arg in args:
        cpprint(arg)


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    for arg in args:
        cpprint(arg)
    exit()
