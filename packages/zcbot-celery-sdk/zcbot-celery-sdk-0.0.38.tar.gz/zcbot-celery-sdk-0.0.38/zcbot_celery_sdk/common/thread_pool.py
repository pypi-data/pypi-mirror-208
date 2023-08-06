import asyncio
import functools
import typing
from concurrent.futures import ThreadPoolExecutor

T = typing.TypeVar('T')

# worker pool starts in main process
_CELERY_TASK_POOL: typing.Optional[ThreadPoolExecutor] = None


def get_worker_pool() -> ThreadPoolExecutor:
    """
    get worker pool instance
    should be executed in main process
    main process -> worker 1 -> task 1
                                task 2
                                task 3
                    worker 2 -> task 1
                                task 2
                                task 3
                    worker 3 -> task 1
                                task 2
                                task 3
    task pool should be released once tasks are finished
    while worker pool should be always held at background
    :return: worker pool instance
    """
    global _CELERY_TASK_POOL
    if not _CELERY_TASK_POOL:
        _CELERY_TASK_POOL = ThreadPoolExecutor(thread_name_prefix='consumer')
    return _CELERY_TASK_POOL


def get_pool_size() -> int:
    """
    :return: worker pool instance
    """
    global _CELERY_TASK_POOL
    if _CELERY_TASK_POOL:
        return _CELERY_TASK_POOL._work_queue.qsize()
    return 0


def submit(func: typing.Callable[..., T],
           *args: typing.Any,
           **kwargs: typing.Any) -> T:
    """
    run single task in worker
    :param func: function
    :param args: args
    :param kwargs: keyword args
    :return: result of the function
    """
    future = get_worker_pool().submit(func, *args)
    return future


async def run_in_worker(func: typing.Callable[..., T],
                        *args: typing.Any,
                        **kwargs: typing.Any) -> T:
    """
    run single task in worker
    :param func: function
    :param args: args
    :param kwargs: keyword args
    :return: result of the function
    """
    loop = asyncio.get_event_loop()
    f = functools.partial(func, **kwargs)
    worker_pool = get_worker_pool()
    return await loop.run_in_executor(worker_pool, f, *args)
