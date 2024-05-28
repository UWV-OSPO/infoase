import os
from dotenv import load_dotenv


def load_env():
    load_dotenv()
    if os.getenv("ENVIRONMENT") is not None:
        load_dotenv(f"./.env.{os.getenv('ENVIRONMENT')}")
