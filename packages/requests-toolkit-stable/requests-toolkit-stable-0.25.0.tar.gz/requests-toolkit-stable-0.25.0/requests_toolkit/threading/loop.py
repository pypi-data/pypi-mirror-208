import threading
from typing import Callable, Any
import concurrent.futures
from concurrent.futures import Future

class ThreadLoop:
    def __init__(self):
        self.__loop__ = concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Thread')
        self.__running_tasks__ = []
        self._inloop_ = True
        self.__loop__.__enter__()

    def get_running_tasks(self):
        return self.__running_tasks__

    def join(self, timeout=10):
        self.__loop__.__exit__(None, None, None)
        # Store futures and their corresponding index
        futures = {future: idx for idx, future in enumerate(self.__running_tasks__)}

        # Initialize an empty list of the same length as params
        ret = [None] * len(self.__running_tasks__)

        for future in concurrent.futures.as_completed(self.__running_tasks__):
            # Get the index of the completed future
            idx = futures[future]

            # Store the result at the appropriate index in ret
            try:
                result = future.result(timeout)
            except concurrent.futures.TimeoutError:
                result = None

            ret[idx] = result

        self.__running_tasks__.clear()
        self._inloop_ = False
        return ret

    def clear(self):
        self.__running_tasks__.clear()

    def sync(self,timeout=10):
        return self.join(timeout)

    def start(self, fn:Callable,kwargs:dict,onComplete: Callable[[Future],Any] = None):
        if not self._inloop_:
            self._inloop_ = True
            self.__loop__.__enter__()

        def wrapper(**kwargs):
            print(f'''>>> Working on {threading.current_thread()}...''')
            return fn(**kwargs)

        future = self.__loop__.submit(wrapper,**kwargs)
        if onComplete is not None:
            future.add_done_callback(onComplete)
        self.__running_tasks__.append(future)
        return future

if __name__ == '__main__':
    from concurrent.futures import Future
    import time

    print_lock = threading.Lock()

    def task():
        time.sleep(5)
        return 5

    def onComplete(future: Future):
        with print_lock:
            print(future.result())

    loop = ThreadLoop()
    a = loop.start(task, dict(), onComplete)
    b = loop.start(task, dict(), onComplete)
    c = loop.start(task, dict(), onComplete)

    print(loop.sync())


