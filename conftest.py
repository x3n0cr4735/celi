import os

from celi_framework.logging_setup import setup_logging
from celi_framework.utils.llm_cache import enable_llm_caching
from dotenv import load_dotenv

load_dotenv()
os.environ["PYTHONASYNCIODEBUG"] = "1"

setup_logging()
enable_llm_caching()
