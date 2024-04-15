import os
from requests_cache import CachedSession
from celi_framework.utils.utils import get_cache_dir


def get_cached_session() -> CachedSession:
    """Returns a singleton cached session for HTTP requests."""
    if not hasattr(get_cached_session, "_session"):
        cache_dir = get_cache_dir()
        session = CachedSession(
            os.path.join(cache_dir, "http_cache.sqlite"),
            backend="sqlite",
            cache_control=True,
        )
        get_cached_session._session = session
    return get_cached_session._session
