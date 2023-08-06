from colorama import Fore, Style


def print_failure(text, end="\n"):
    """Print a failure message."""

    print(Fore.RED, text, Style.RESET_ALL, sep="", end=end)


def print_partialsuccess(text, end="\n"):
    """Print a partial sucess message."""

    print(Fore.MAGENTA, text, Style.RESET_ALL, sep="", end=end)


def print_success(text, end="\n"):
    """Print a success message."""

    print(Fore.GREEN, text, Style.RESET_ALL, sep="", end=end)


def print_info(text, sep="", end="\n"):
    """Print a success message."""

    print(text, sep, end=end)
