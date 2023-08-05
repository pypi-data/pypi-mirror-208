# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:12:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Decorators.
"""


from typing import Any, Tuple, Callable, Optional, Union, Literal, overload
from tqdm import tqdm as tqdm_tqdm
from threading import Thread
from functools import wraps as functools_wraps

from .rbase import exc
from .rtext import rprint
from .rdatetime import RDateTimeMark, now
from . import roption


def wrap_frame(decorator: Callable) -> Callable:
    """
    Decorative frame.

    Parameters
    ----------
    decorator : Decorator function.

    Retuens
    -------
    Decorator after decoration.

    Examples
    --------
    Decoration function method one.
    >>> @wrap_func
    >>> def func(): ...
    >>> result = func(param_a, param_b, param_c=1, param_d=2)

    Decoration function method two.
    >>> def func(): ...
    >>> result = wrap_func(func, param_a, param_b, param_c=1, param_d=2)

    Decoration function method three.
    >>> def func(): ...
    >>> result = wrap_func(func, _execute=True)
    
    Decoration function method four.
    >>> def func(): ...
    >>> func = wrap_func(func)
    >>> result = func(param_a, param_b, param_c=1, param_d=2)

    Decoration function method five.
    >>> def func(): ...
    >>> func = wrap_func(func, param_a, param_c=1, _execute=False)
    >>> result = func(param_b, param_d=2)
    """

    # Decorate Decorator.
    @functools_wraps(decorator)
    def wrap(func: Callable, *args: Any, _execute: Optional[bool] = None, **kwargs: Any) -> Union[Callable, Any]:
        """
        Decorative shell.

        Parameters
        ----------
        _execute : Whether execute function, otherwise decorate function.
            - None : When parameter 'args' or 'kwargs' have values, then True, otherwise False.
            - bool : Use this value.
        
        Returns
        -------
        Function after decoration or return of function.
        """

        # Handle parameters.
        if _execute == None:
            if args != () or kwargs != {}:
                _execute = True
            else:
                _execute = False

        # Direct execution.
        if _execute:
            result = decorator(func, *args, **kwargs)
            return result

        # Decorate function.
        @functools_wraps(func)
        def wrap_sub(*_args: object, **_kwargs: object) -> object:
            """
            Decorative sub shell.
            """

            # Decorate function.
            result = decorator(func, *args, *_args, **kwargs, **_kwargs)

            return result

        return wrap_sub

    return wrap


def wraps(*wrap_funcs: Callable) -> Callable:
    """
    Batch decorate.

    Parameters
    ----------
    wrap_funcs : Decorator function.

    Retuens
    -------
    Function after decoration.

    Examples
    --------
    Decoration function.
    >>> @wraps(print_funtime, state_thread)
    >>> def func(): ...
    >>> result = func()

        Same up and down

    >>> @print_funtime
    >>> @state_thread
    >>> def func(): ...
    >>> result = func()

        Same up and down

    >>> def func(): ...
    >>> func = print_funtime(func)
    >>> func = state_thread(func)
    >>> result = func()
    """

    # Sequential decorate.
    def func(): ...
    for wrap_func in wrap_funcs:

        ## One shell.
        @functools_wraps(func)
        def wrap(func: Callable) -> Callable:
            """
            Decorative shell
            """

            ## Two shell.
            @functools_wraps(func)
            def wrap_sub(*args: object, **kwargs: object) -> object:
                """
                Decorative sub shell
                """

                # Decorate.
                result = wrap_func(func, *args, _execute=True, **kwargs)

                return result

            return wrap_sub

        func = wrap

    return wrap


@overload
def runtime(func: Callable, *args: Any, _return_report: bool = False, **kwargs: Any) -> Union[Any, Tuple[Any, str]]: ...

@overload
def runtime(_return_report: Literal[False]) -> Any: ...

@overload
def runtime(_return_report: Literal[True]) -> Union[Any, Tuple[Any, str]]: ...

@wrap_frame
def runtime(func: Callable, *args: Any, _return_report: bool = False, **kwargs: Any) -> Union[Any, Tuple[Any, str]]:
    """
    Print or return runtime report of the function.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position parameter of input parameter decorated function.
    _return_report : Whether return report, otherwise print report.
    kwargs : Keyword parameter of input parameter decorated function.

    Returns
    -------
    Function execute result or runtime report.
    """

    # Execute function and marking time.
    rtm = RDateTimeMark()
    result = func(*args, **kwargs)
    rtm.mark()

    # Generate report.
    runtime = rtm.record[-1]["interval_timestamp"] / 1000
    report = "Start: %s -> Spend: %ss -> End: %s" % (
        rtm.record[0]["datetime_str"],
        runtime,
        rtm.record[1]["datetime_str"]
    )
    title = func.__name__

    # Return report.
    if _return_report:
        return result, report

    # Print report.
    rprint(report, title=title)

    return result


@overload
def start_thread(func: Callable, *args: Any, _daemon: bool = True, **kwargs: Any) -> Thread: ...

@wrap_frame
def start_thread(func: Callable, *args: Any, _daemon: bool = True, **kwargs: Any) -> Thread:
    """
    Function start in thread.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position parameter of input parameter decorated function.
    _daemon : Whether it is a daemon thread.
    kwargs : Keyword parameter of input parameter decorated function.

    Returns
    -------
    Thread object.
    """

    # Handle parameters.
    thread_name = "%s_%d" % (func.__name__, now("timestamp"))

    # Create thread.
    thread = Thread(target=func, name=thread_name, args=args, kwargs=kwargs)
    thread.daemon = _daemon

    # Start thread.
    thread.start()

    return thread


@overload
def try_exc(func: Callable, *args: Any, **kwargs: Any) -> Optional[Any]: ...

@wrap_frame
def try_exc(func: Callable, *args: Any, **kwargs: Any) -> Optional[Any]:
    """
    Execute function with 'try' syntax and print error information.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position parameter of input parameter decorated function.
    kwargs : Keyword parameter of input parameter decorated function.

    Returns
    -------
    Function execute result or no return.
    """

    # Execute function.
    try:
        result = func(*args, **kwargs)

    # Print error information.
    except:
        func_name = func.__name__
        exc(func_name)

    # Return function result.
    else:
        return result


@overload
def update_tqdm(
    func: Callable,
    tqdm: tqdm_tqdm,
    *args: Any,
    _desc: Optional[str] = None,
    _step: Union[int, float] = 1,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def update_tqdm(
    func: Callable,
    tqdm: tqdm_tqdm,
    *args: Any,
    _desc: Optional[str] = None,
    _step: Union[int, float] = 1,
    **kwargs: Any
) -> Any:
    """
    Update progress bar tqdm object of tqdm package.

    Parameters
    ----------
    func : Function to be decorated.
    tqdm : Progress bar tqdm object.
    args : Position parameter of input parameter decorated function.
    _desc : Progress bar description.
        - None : no description.
        - str : Add description.

    _step : Progress bar step size.
        - When greater than 0, then forward.
        - When less than 0, then backward.

    kwargs : Keyword parameter of input parameter decorated function.

    Returns
    -------
    Function execute result.
    """

    # Set description.
    if _desc != None:
        tqdm.set_description(_desc)

    # Execute function.
    result = func(*args, **kwargs)

    # Update progress bar.
    tqdm.update(_step)

    return result


@overload
def retry(
    func: Callable,
    *args: Any,
    _report: Optional[str] = None,
    _handle: Optional[Callable] = None,
    _exception: Union[BaseException, Tuple[BaseException, ...]] = BaseException,
    _try_total: int = 1,
    _try_count: int = 0,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def retry(
    func: Callable,
    *args: Any,
    _report: Optional[str] = None,
    _handle: Optional[Callable] = None,
    _exception: Union[BaseException, Tuple[BaseException, ...]] = BaseException,
    _try_total: int = 1,
    _try_count: int = 0,
    **kwargs: Any
) -> Any:
    """
    Try again.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position parameter of input parameter decorated function.
    _report : Print report title.
        - None : Not print.
        - str : Print and use this title.

    _handle : Pre handle function before retrying.
        - None : Not handle.
        - Callable : Execute function.

    _exception : Catch exception types.
    _try_total : Retry total.
    _try_count : Retry count.
    kwargs : Keyword parameter of input parameter decorated function.

    Returns
    -------
    Function execute result.
    """

    # Pre handle.
    if _handle != None and _try_count != 0:
        _handle()

    # Execute.

    ## Try count full.
    if _try_count > _try_total:
        result = result = func(*args, **kwargs)

    ## Try count not full.
    else:

        ### Try.
        try:
            result = func(*args, **kwargs)
        except _exception:

            ### Report.
            if _report != None:
                error_msg, _, _, _ = exc()
                rprint(
                    error_msg,
                    "Retrying...",
                    title=_report,
                    frame="half"
                )

            ### Retry.
            _try_count += 1
            result = retry(
                func,
                *args,
                _report=_report,
                _handle=_handle,
                _exception=_exception,
                _try_total=_try_total,
                _try_count=_try_count,
                **kwargs
            )

    return result