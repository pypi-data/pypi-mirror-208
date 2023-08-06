
class InvalidConfigException(Exception):
    """Raised when an invalid configuration is encountered."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidDataTypeException(Exception):
    """Raised when an invalid data type is encountered."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class FileNotFoundException(Exception):
    """Raised when a file is not found."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
