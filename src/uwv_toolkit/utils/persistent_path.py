import os
from .load_env import load_env


def persistent_path(path: str = None, force_create: bool = False) -> str:
    """
    Returns the storage path for the given path, optionally creating the directory if it doesn't exist.

    Args:
        path (str, optional): The subdirectory path within the storage directory. Defaults to None.
        force_create (bool, optional): Whether to create the directory if it doesn't exist. Defaults to False.

    Returns:
        str: The storage path.


    Usage:
    # Get the storage path
    path = persistent_path()

    # Get the storage path with a subdirectory
    path = persistent_path("subdirectory")
    """

    load_env()

    if path is None:
        directory = os.environ["PERSISTENT_STORAGE_PATH"]
    else:
        directory = os.path.join(os.environ["PERSISTENT_STORAGE_PATH"], path)

    if force_create and not os.path.exists(directory):
        os.makedirs(directory)

    return directory
