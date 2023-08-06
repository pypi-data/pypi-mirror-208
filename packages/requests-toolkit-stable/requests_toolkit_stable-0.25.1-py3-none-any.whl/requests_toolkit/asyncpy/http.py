from .loop import ThreadPoolLoop
import aiohttp

class HTTPLoop(ThreadPoolLoop):
    @classmethod
    async def __process_response__(cls,response):
        content_type = response.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            # 响应是JSON数据
            data = await response.json()
            # 对数据进行处理
            return data

        elif content_type and 'text/html' in content_type:
            # 响应是HTML文档
            text = await response.text()
            return text

        else:
            # 响应类型未知
            # 处理错误
            # ...
            return IOError("Unknown content type")

    @classmethod
    async def __GET__(cls,url,headers,params,timeout,ssl):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,headers=headers,params=params,timeout=timeout,ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __POST__(cls,url, headers, data,json, timeout, ssl):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=data,json=json , timeout=timeout, ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __PUT__(cls, url, headers=None, data=None, timeout=10, ssl=None):
        async with aiohttp.ClientSession() as session:
            async with session.put(url=url, headers=headers, data=data, timeout=timeout,
                                   ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __PATCH__(cls, url, headers=None, data=None, timeout=10, ssl=None):
        async with aiohttp.ClientSession() as session:
            async with session.patch(url=url, headers=headers, data=data, timeout=timeout,
                                     ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __DELETE__(cls, url, headers=None, timeout=10, ssl=None):
        async with aiohttp.ClientSession() as session:
            async with session.delete(url=url, headers=headers, timeout=timeout,
                                      ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __HEAD__(cls, url,allow_redirects:bool=False ,headers=None, timeout=10, ssl=None):
        async with aiohttp.ClientSession() as session:
            async with session.head(url=url, headers=headers,allow_redirects=allow_redirects, timeout=timeout,
                                    ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    @classmethod
    async def __OPTIONS__(cls, url, headers=None,allow_redirects:bool=False , timeout=10, ssl=None):
        async with aiohttp.ClientSession() as session:
            async with session.options(url=url, headers=headers, allow_redirects=allow_redirects, timeout=timeout,
                                       ssl=ssl) as response:
                result = await cls.__process_response__(response)
                if response.status == 200:
                    return result
                else:
                    return IOError(result)

    def get(self,url,headers=None,params=None,timeout=None,ssl=False):
        self.start_new_task(self.__GET__,url,headers,params,timeout,ssl)

    def post(self,url,headers=None,data=None,json=None, timeout=None,ssl=False):
        self.start_new_task(self.__POST__,url,headers,data,json,timeout,ssl)

    def put(self, url, headers=None, data=None, timeout=None, ssl=False):
        self.start_new_task(self.__PUT__, url, headers, data, timeout, ssl)

    def patch(self, url, headers=None, data=None, timeout=None, ssl=False):
        self.start_new_task(self.__PATCH__, url, headers, data, timeout, ssl)

    def delete(self, url, headers=None, timeout=None, ssl=False):
        self.start_new_task(self.__DELETE__, url, headers, timeout, ssl)

    def head(self, url, headers=None, allow_redirects:bool=False , timeout=None, ssl=False):
        self.start_new_task(self.__HEAD__, url, allow_redirects, headers, timeout, ssl)

    def options(self, url, headers=None, allow_redirects:bool=False , timeout=None, ssl=False):
        self.start_new_task(self.__OPTIONS__, url, headers, allow_redirects, timeout, ssl)



