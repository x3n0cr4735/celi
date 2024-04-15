import atexit
import json
import logging.config
import os
from pathlib import Path

from dotenv import load_dotenv

from celi_framework.logging_setup import setup_logging

load_dotenv()
os.environ["PYTHONASYNCIODEBUG"] = "1"

# Set up logging
setup_logging()
