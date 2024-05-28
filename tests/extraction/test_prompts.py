import os
from modules.extraction import prompts
from modules.utils import Utilities
from modules.utils.load_env import load_env

load_env()


def test_extraction_prompt():
    clean_prompt = prompts.extraction_prompt.format(input="<TEKST HIER")
    if os.environ.get("VERBOSE") == "1":
        print(clean_prompt)

    file = f"{Utilities.persistent_storage_path()}/prompts/extraction_prompt.txt"
    if not os.path.exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)

    # Save to tmp/prompts/extraction_prompt.txt
    with open(file, "w", encoding="utf-8") as f:
        f.write(clean_prompt)
