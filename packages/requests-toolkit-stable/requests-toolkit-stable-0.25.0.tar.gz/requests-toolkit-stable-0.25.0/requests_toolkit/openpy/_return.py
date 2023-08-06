from typing import Awaitable
import asyncio
from ..utils import in_jupyter_notebook

class BaseReturn:
    def __init__(self,data):
        '''
        Only accept key word arguments and store every argument as an attribute
        :param kwargs:
        '''
        self.data = data

    def eval(self):
        '''
        evaluate self
        :return:
        '''
        return self.data

    # subscriptable and slice-able
    def __getitem__(self, idx):
        return self.eval()[idx]

    # return an iterator that can be used in for loop etc.
    def __iter__(self):
        return self.eval().__iter__()

    def __len__(self):
        return len(self.eval())

    def __eq__(self, other):
        return self.eval().__eq__(other)

    def __str__(self) -> str:
        return str(self.eval())

    def __repr__(self):
        return repr(self.eval())


class AsyncReturn(BaseReturn, Awaitable):
    def __init__(self, task:Awaitable):
        super().__init__(task)
        self.value = None

    def eval(self):
        if self.value is not None:
            return self.value

        if in_jupyter_notebook():
            self.value = self.data  # jupyter: need await
        else:
            self.value = asyncio.get_event_loop().run_until_complete(self.data)  # script
        return self.value

    def __await__(self):
        return self.data.__await__()
