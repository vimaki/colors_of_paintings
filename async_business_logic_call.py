"""Asynchronous function call extracting the primary colors of the image.

Run in the default loop's executor the function 'get_primary_colors'
from module 'get_primary_colors'.

Functions
---------
wrapper_get_colors
    Returns get_primary_colors with fixed parameters.
async_get_colors
    Asynchronous start of get_primary_colors.

References
----------
get_primary_colors.py
    Module with synchronous business logic.
"""

import asyncio
import numpy as np
from collections.abc import Callable
from functools import partial
from typing import List

import get_primary_colors


def wrapper_get_colors(*args, **kwargs) -> Callable[..., List[np.array]]:
    """Returns get_primary_colors with fixed parameters."""
    new_get_colors = partial(get_primary_colors.get_primary_colors,
                             *args, **kwargs)
    return new_get_colors


async def async_get_colors(*args, **kwargs) -> None:
    """Asynchronous start of get_primary_colors."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, wrapper_get_colors(*args, **kwargs))
