# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-19 20:06:20
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Multi task methods.
"""


from typing import Callable, Any, Generator, Optional
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from .rwrap import update_tqdm


def threads(
    func: Callable,
    *args: Any,
    max_workers: Optional[int] = None,
    thread_name: Optional[str] = None,
    timeout: Optional[int] = None,
    to_tqdm: bool = True,
    **kwargs: Any
) -> Generator:
    """
    Concurrent `multi tasks` using thread pool.

    Parameters
    ----------
    func : Task function.
    args : Position parameter of input parameter task function.
    max_workers: Maximum number of threads.
        - `None` : Number of CPU + 4, 32 maximum.
        - `int` : Use this value, no maximum limit.

    thread_name: Thread name prefix and progress bar description.
        - `None` : Thread name prefix is `ThreadPoolExecutor-%d` % index, and no progress bar.
        - `str` : Use this value.

    timeout : Call generator maximum waiting second, overdatetime throw error.
        - `None` : Unlimited.
        - `int` : Use this value.

    to_tqdm : Whether print progress bar.
    kwargs : Keyword parameter of input parameter task function.
    
    Returns
    -------
    Generator with multi Future object, object from concurrent package.
    When called, it will block until all tasks are completed.
    When `for` syntax it, the task that complete first return first.

    Examples
    --------
    Get value.
    >>> results = [future.result() for future in Generator]
    """

    # Handle parameters.
    if thread_name == None:
        thread_name = func.__name__
    params_lens = {len(param) for param in args}
    params_lens -= {1}
    min_param_len = min(params_lens)
    args = [
        list(param) * min_param_len
        if len(param) == 1
        else param
        for param in args
    ]
    kwargs = [
        [[key, val]] * min_param_len
        if len(val) == 1
        else [
            [key, param]
            for param in val
        ]
        for key, val in kwargs.items()
    ]
    if args:
        args = zip(*args)
    else:
        args = [[]] * min_param_len
    if kwargs:
        kwargs = zip(*kwargs)
        kwargs = [dict(param) for param in kwargs]
    else:
        kwargs = [{}] * min_param_len
    params = zip(args, kwargs)

    # Create thread pool.
    thread_pool = ThreadPoolExecutor(max_workers, thread_name)

    # Add progress bar.
    if to_tqdm:
        tqdm_desc = "ThreadPool " + thread_name
        obj_tqdm = tqdm(desc=tqdm_desc, total=min_param_len)
        func = update_tqdm(func, obj_tqdm, _execute=False)

    # Start thread pool.
    tasks = [thread_pool.submit(func, *args, **kwargs) for args, kwargs in params]

    # Return generator.
    obj_tasks = as_completed(tasks, timeout)
    return obj_tasks