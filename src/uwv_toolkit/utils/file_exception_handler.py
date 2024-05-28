import os
from datetime import datetime
import traceback
import logging
from .load_env import load_env
from .persistent_path import persistent_path


class FileExceptionHandler:
    """
    This class handles exceptions by writing them to a file.

    Example:
    try:
        raise Exception("test")
    except Exception as e:
        FileExceptionHandler.handle(exception=e)

        # Display an error message and stop rendering.
        return st.error(
            "An error occurred."
        )
    """

    @staticmethod
    def handle(
        exception: Exception,
        extra_info: str = None,
        filepath: str = None,
    ):
        """
        Handle an exception by writing it to a file and logging it.

        Args:
            exception (Exception): The exception to handle.
            filepath (str, optional): The directory path where the exception file will be saved.
                If not provided, it defaults to the value of the 'PERSISTANT_DIR' environment variable
                or './tmp' if the environment variable is not set.
        """

        if filepath is None:
            load_env()
            filepath = persistent_path("exceptions")

        # Create the exceptions directory if it does not exist
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Create a filename with timestamp
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_exception.txt"

        # Create the filepath
        filepath = str(filepath) + "/" + filename

        exception_log = "EXCEPTION: " + str(exception) + "\n\n"
        exception_log += "TRACEBACK: " + str(traceback.format_exc()) + "\n\n"
        if extra_info:
            exception_log += "EXTRA INFO: " + extra_info + "\n\n"

        # Write the exception to a file
        with open(filepath, "a") as exception_file:
            exception_file.write(exception_log)

        logging.exception(exception, exc_info=True)

        if os.getenv("VERBOSE") == "1":
            print(f"An exception has been written to {filepath}")
            print(exception_log)
