import os
from datetime import datetime
import traceback
import logging
from modules.utils.load_env import load_env

load_env()


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
        filepath: str = f"{os.getenv('PERSISTENT_STORAGE_PATH', './tmp')}/exceptions/",
    ):
        # Create the exceptions directory if it does not exist
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Create a filename with timestamp
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_exception.txt"

        # Create the filepath
        filepath = str(filepath) + "/" + filename

        # Write the exception to a file
        with open(filepath, "a") as exception_file:
            exception_file.write("EXCEPTION:\n")
            exception_file.write(str(exception))
            exception_file.write("\n\n")
            exception_file.write("TRACEBACK:\n")
            exception_file.write(traceback.format_exc())

        logging.exception(exception, exc_info=True)
