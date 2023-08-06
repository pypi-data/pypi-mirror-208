from dotenv import load_dotenv as py_load_dotenv  # type: ignore
import os


def load_dotenv() -> None:
    py_load_dotenv()


def value(key: str) -> str: return os.getenv(key) or ''
