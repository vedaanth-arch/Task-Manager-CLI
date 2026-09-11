import json
from pathlib import Path


TOKEN_FILE = Path.home() / ".task_manager_tokens.json"


def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as file:
        json.dump(tokens, file)


def load_tokens():
    if not TOKEN_FILE.exists():
        return None

    with open(TOKEN_FILE, "r") as file:
        return json.load(file)


def logout():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()