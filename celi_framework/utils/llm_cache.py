import asyncio
import json
import logging
import random
import shutil
from pathlib import Path

import aiosqlite

from celi_framework.utils.utils import generate_hash_id, get_cache_dir

logger = logging.getLogger(__name__)

_global_llm_cache = None


def enable_llm_caching(simulate_live: bool = False):
    """Enables LLM caching for all calls using the celi_framework.utils.llms functions.

    If simulate_live is set to true, imposes a delay on each call to simulate live calls.  Useful when testing timing
    or for demos.
    """
    global _global_llm_cache
    _global_llm_cache = LLMCache(simulate_live)


def get_celi_llm_cache():
    """
    A function that retrieves the global LLM cache.
        """
    return _global_llm_cache


class LLMCache:
    def __init__(self, simulate_live: bool = False):
        """
        Initializes the LLMCache object.

        Parameters:
            simulate_live (bool): Flag to indicate whether to simulate live calls.

        Returns:
            None
        """
        dir = get_cache_dir()
        self.cache_file = dir / "llm_cache.db"
        if not self.cache_file.exists():
            logger.info("LLM Cache file didn't exist, copying seed file.")
            shutil.copy(Path(__file__).parent / "seed_llm_cache.db", self.cache_file)
        self.cache_delay = 3.0 if simulate_live else None
        self._connection = None
        self._lock = asyncio.Lock()

    async def connection(self):
        """
        A coroutine that establishes a connection to the database. 
        If the connection is not already established, it creates a new connection using aiosqlite. 
        Additionally, it creates the 'llm_cache' table if it does not already exist in the database. 
        Returns the connection object.
        """
        if self._connection is None:
            async with self._lock:
                if self._connection is None:
                    self._connection = await aiosqlite.connect(
                        self.cache_file, isolation_level=None
                    )
                    # Create llm_cache table if it doesn't exist
                    await self._connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS llm_cache (
                            _id TEXT PRIMARY KEY,
                            response TEXT NOT NULL
                        )
                        """
                    )
        return self._connection

    async def close(self):
        """
        A coroutine that closes the connection to the database if it's currently open.
        """
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def check_llm_cache(self, **kwargs):
        """
        A coroutine that checks if the id is in the cache and returns the cache entry if found, False otherwise.
        """
        id = generate_hash_id(kwargs)
        # Check if the id is in the cache.  Return the cache entry if it is, False otherwise.
        c = await self.connection()
        cursor = await c.execute("SELECT response FROM llm_cache WHERE _id = ?", (id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        else:
            if self.cache_delay:
                await asyncio.sleep(self.randomize_delay(self.cache_delay))
            return json.loads(row[0])

    async def cache_llm_response(self, response: dict, **kwargs):
        """
        Caches the given LLM response in the database.

        Args:
            response (dict): The LLM response to cache.
            **kwargs: Additional keyword arguments to generate the cache ID.

        Returns:
            None
        """
        id = generate_hash_id(kwargs)
        s = json.dumps(response)
        c = await self.connection()
        await c.execute("INSERT INTO llm_cache (_id, response) VALUES (?, ?)", (id, s))

    @staticmethod
    def randomize_delay(starting_delay: float):
        """
        Generates a random delay by applying a percentage variation to the starting delay.

        Args:
            starting_delay (float): The initial delay value.

        Returns:
            float: The randomized delay value.
        """
        percentage = random.uniform(-20, 20) / 100
        return starting_delay * (1 + percentage)
