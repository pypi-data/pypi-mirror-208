import asyncio
import random
import threading
from asyncio import Task
from typing import List, Union,Dict,Callable


class BasisLoop:
    def __init__(self):
        try:
            self.__loop__ = asyncio.get_event_loop()
        except:
            self.__loop__ = asyncio.new_event_loop()
        self.__tasks__ = []

    def get_all_tasks(self):
        return self.__tasks__
    def get_done_tasks(self):
        return list(filter(lambda x: x.done(), self.__tasks__))
    def get_cancelled_tasks(self):
        return list(filter(lambda x: x.cancelled(), self.__tasks__))
    def get_pending_tasks(self):
        return list(filter(lambda x:not x.cancelled() and not x.done(), self.__tasks__))
    def wait_all_done(self):
        return self.join()
    def join(self):
        return [self.__loop__.run_until_complete(t) for t in self.__tasks__]
    def clear(self):
        self.__tasks__.clear()
    def get_task_statues(self):
        return [t._state for t in self.__tasks__]
    def sync(self):
        return self.join()

    @staticmethod
    def __create_coro__(async_func, *args):
        return async_func(*args)

class PendingLoop(BasisLoop):
    '''
    example usage:
    asyncpy def dumi():
        print(0)
        await asyncio.sleep(1)
        print(1)


    loop = PendingLoop()
    loop.pend_new_task(dumi()) # task not started
    loop.pend_new_task(dumi()) # task not started
    loop.pend_new_task(dumi()) # task not started
    loop.wait_all_done()
    '''
    def __init__(self):
        super().__init__()

    def pend_new_task(self, coro, name=None) ->Task:
        task = self.__loop__.create_task(coro)
        if name is not None:
            task.set_name(name)
        self.__tasks__.append(task)
        return task

    def __pend_dumi_tasks__(self, n_tasks: int) -> List[Task]:
        async def dumi():
            print('task started')
            t = random.randint(0,10)
            await asyncio.sleep(t)
            print(f'task finished. Use time {t} seconds.')

        return [self.pend_new_task(dumi()) for _ in range(n_tasks)]


class ThreadPoolLoop(PendingLoop):
    '''
    example usage:

    import random
    asyncpy def dumi():
        print('task started')
        t = random.randint(0, 10)
        await asyncio.sleep(t)
        print(f'task finished. Use time {t} seconds.')

    loop = ThreadPoolLoop()
    loop.start_new_task(dumi) # task started
    loop.start_new_task(dumi)  # task started
    loop.start_new_task(dumi)  # task started

    loop.yield_done(print)
    '''
    def __init__(self):
        super().__init__()

    def start_new_task(self, async_func, *func_args, task_name:str=None):
        async def afun_ext():
            print(f"Thread ID: {threading.current_thread().ident}, Thread Name: {threading.current_thread().name}")
            return await async_func(*func_args)

        async def create_task():
            # coro = await self.__loop__.run_in_executor(None, self.__create_coro__, afun_ext) # 验证只有一个线程
            coro = await self.__loop__.run_in_executor(None, self.__create_coro__, async_func,*func_args)
            task = self.__loop__.create_task(coro)
            if task_name is not None:
                task.__name__ = task_name
            else:
                task.__name__ = f'Task {len(self.__tasks__)}'

            self.__tasks__.append(task)
            return task
        return self.__loop__.run_until_complete(create_task())

    async def __yield_done_generator__(self):
        """Async generator that yields completed tasks from a list of tasks."""
        completed = set()
        tasks = self.__tasks__
        while tasks:
            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done - completed:
                completed.add(task)
                yield task

    def yield_done(self, callback:Union[Callable,Dict]):
        async def wrapper():
            async for t in self.__yield_done_generator__():
                print(f"{t.__name__} finished.")
                if isinstance(callback,dict):
                    callback_ = callback[t.__name__]
                    callback_(t.result())
                else:
                    callback(t.result())

        task= self.__loop__.create_task(wrapper())
        self.__loop__.run_until_complete(task)










