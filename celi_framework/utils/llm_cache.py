import asyncio
import json
import random
import shutil
from pathlib import Path

import aiosqlite

from celi_framework.utils.utils import generate_hash_id, get_cache_dir

_global_llm_cache = None


def enable_llm_caching(simulate_live: bool = False):
    """Enables LLM caching for all calls using the celi_framework.utils.llms functions.

    If simulate_live is set to true, imposes a delay on each call to simulate live calls.  Useful when testing timing
    or for demos.
    """
    global _global_llm_cache
    _global_llm_cache = LLMCache(simulate_live)


def get_celi_llm_cache():
    return _global_llm_cache


class LLMCache:
    def __init__(self, simulate_live: bool = False):
        dir = get_cache_dir()
        self.cache_file = dir / "llm_cache.db"
        if not self.cache_file.exists():
            shutil.copy(Path(__file__).parent / "seed_llm_cache.db", self.cache_file)
        self.cache_delay = 3.0 if simulate_live else None
        self._connection = None
        self._lock = asyncio.Lock()

    async def connection(self):
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
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def check_llm_cache(self, **kwargs):
        id = generate_hash_id(kwargs)
        # Check if the id is in the cache.  Return the cache entry if it is, False otherwise.classmethod
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
        id = generate_hash_id(kwargs)
        s = json.dumps(response)
        c = await self.connection()
        await c.execute("INSERT INTO llm_cache (_id, response) VALUES (?, ?)", (id, s))

    @staticmethod
    def randomize_delay(starting_delay: float):
        percentage = random.uniform(-20, 20) / 100
        return starting_delay * (1 + percentage)
