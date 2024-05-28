import os
from dotenv import load_dotenv


def is_test_env() -> bool:
    """
    Returns True if the environment is set to test.

    Returns:
        bool: True if the environment is set to test.
    """
    return os.getenv("ENVIRONMENT") == "test"


def is_dev_env() -> bool:
    """
    Returns True if the environment is set to development.

    Returns:
        bool: True if the environment is set to development.
    """
    return os.getenv("ENVIRONMENT") == "development"


def is_prod_env() -> bool:
    """
    Returns True if the environment is set to production.

    Returns:
        bool: True if the environment is set to production.
    """
    return os.getenv("ENVIRONMENT") == "production"


def load_env() -> None:
    """
    Loads environment variables from the .env file and an optional environment-specific .env file.

    Raises:
        FileNotFoundError: If no .env file is found.
    """
    if not os.path.exists(".env") and not is_prod_env():
        raise FileNotFoundError("No .env config file found")

    load_dotenv()
    if os.getenv("ENVIRONMENT") is not None:
        load_dotenv(f"./.env.{os.getenv('ENVIRONMENT')}")
