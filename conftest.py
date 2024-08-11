import asyncio
import os

import pytest
from dotenv import load_dotenv

from celi_framework.logging_setup import setup_logging
from celi_framework.utils.llm_cache import enable_llm_caching, get_celi_llm_cache

load_dotenv()
os.environ["PYTHONASYNCIODEBUG"] = "1"

setup_logging()
enable_llm_caching()


@pytest.fixture(scope="session", autouse=True)
def cleanup_tests(request):
    """
    A fixture that runs `log_and_cancel_pending_tasks` after all tests have completed.
    """

    def fin():
        asyncio.run(get_celi_llm_cache().close())

    request.addfinalizer(fin)
