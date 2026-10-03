class Cprint:
    # ANSI escape codes for colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    @classmethod
    def colored(cls, message: str, color):
        return f"{color}{message}{cls.RESET}"

    @classmethod
    def print(cls, message: str, color):
        print(cls.colored(message, color))
