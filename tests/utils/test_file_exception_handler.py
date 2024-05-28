import os
from src.modules.utils.file_exception_handler import FileExceptionHandler


def test_file_exception_handler(tmp_path):
    # Create a temporary directory for testing
    tmp_dir = tmp_path

    # Create a test exception

    # Create a test error message
    test_error = "Test error message you won't find elsewhere!"

    test_exception = ValueError(test_error)

    # Create a FileExceptionHandler instance
    file_exception_handler = FileExceptionHandler()

    # Call the handle method with the test exception and error message
    file_exception_handler.handle(test_exception, filepath=tmp_dir)

    # Get the list of files in the temporary directory
    files = os.listdir(tmp_dir)

    # Assert that a single file was created
    assert len(files) == 1

    # Get the filepath of the created file
    filepath = os.path.join(tmp_dir, files[0])

    # Assert that the file exists
    assert os.path.exists(filepath)

    # Read the contents of the file
    with open(filepath, "r") as exception_file:
        content = exception_file.read()

    # Assert that the exception and error message are written to the file
    assert str(test_exception) in content
    assert test_error in content
