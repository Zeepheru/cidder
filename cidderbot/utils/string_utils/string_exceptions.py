class InvalidAnsiColorCodeException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        if message:
            super().__init__("Supplied ANSI color code is incorrect: " + message)
        else:
            super().__init__("Supplied ANSI color code is incorrect")
