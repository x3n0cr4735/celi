import os

from dotenv import load_dotenv

from celi_framework.logging_setup import setup_logging

load_dotenv()
os.environ["PYTHONASYNCIODEBUG"] = "1"

setup_logging()
