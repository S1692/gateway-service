"""
Supabase client management.

This module provides a small helper to construct and cache a Supabase client.  It
reads the Supabase URL and anon key from environment variables.  If either
variable is missing, a runtime error will be raised.  The `get_supabase`
function can be used as a FastAPI dependency to inject the client into your
endpoints.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Generator

from fastapi import Depends

# We intentionally avoid importing supabase at module load time.  Importing it
# eagerly would raise an ImportError in environments where the library is not
# installed (e.g. during testing), preventing the application from starting.
# Instead we perform the import inside `get_supabase_client` when the client
# is actually needed.  This makes the database layer optional: the root
# endpoint does not depend on Supabase.


@lru_cache()
def get_supabase_client():
    """
    Create and cache the Supabase client.

    The Supabase client is created lazily so that tests not involving the
    database can run without the `supabase-py` package installed.  When
    invoked, the function reads the `SUPABASE_URL` and `SUPABASE_ANON_KEY`
    environment variables and attempts to import the `supabase` module.  If
    either variable is missing or the module import fails, a `RuntimeError`
    is raised.
    """

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in the environment."
        )
    try:
        # Import supabase lazily.  We cannot annotate the return type as
        # `supabase.Client` here because the module may not be available when
        # type checking is performed.
        from supabase import create_client  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "supabase-py is required for database operations. Please install it via 'pip install supabase-py'."
        ) from exc
    return create_client(url, key)


def get_supabase():
    """
    FastAPI dependency to retrieve the cached Supabase client.

    Returns
    -------
    supabase.Client
        A configured Supabase client.
    """

    return get_supabase_client()