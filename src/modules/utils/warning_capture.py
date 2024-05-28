import warnings


class WarningCapture:
    """
    This class captures warnings that are raised during a with statement.

    Example usage:
    with WarningCapture() as wc:
        warnings.warn("Example warning 1")
        warnings.warn("Example warning 2")

    The captured warnings can be accessed through the `captured_warnings` attribute.

    Example:
    for warn in wc.captured_warnings:
        print(warn)
    """

    def __init__(self):
        self.captured_warnings = []
        self.original_showwarning = warnings.showwarning

    def showwarning(self, message, category, filename, lineno, file=None, line=None):
        """
        Callback function used to capture warnings.

        Args:
            message (str): The warning message.
            category (Warning): The warning category.
            filename (str): The name of the file where the warning occurred.
            lineno (int): The line number where the warning occurred.
            file (file-like object, optional): The file object where the warning is written to. Defaults to None.
            line (str, optional): The line of code where the warning occurred. Defaults to None.
        """
        self.captured_warnings.append(
            f"{category.__name__}: {message} at line {lineno} in {filename}"
        )

    def __enter__(self):
        warnings.showwarning = self.showwarning
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        warnings.showwarning = self.original_showwarning
