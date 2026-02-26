import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus-08-2024")
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
    DEFAULT_OUTPUT_DIR = Path(os.getenv("DEFAULT_OUTPUT_DIR", BASE_DIR / "output"))
    DICTIONARY_FILE = Path(os.getenv("DICTIONARY_FILE", BASE_DIR / "replacement_dictionary.json"))
