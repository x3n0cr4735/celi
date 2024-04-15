class ContextLengthExceededException(Exception):
    """Exception raised when the input exceeds the model's maximum context length."""

    def __init__(self, message="Context length exceeded the model's maximum limit."):
        self.message = message
        super().__init__(self.message)


class ParsingException(Exception):
    """
    Custom exception raised for errors encountered during the parsing of responses or prompt completions.
    """

    pass
