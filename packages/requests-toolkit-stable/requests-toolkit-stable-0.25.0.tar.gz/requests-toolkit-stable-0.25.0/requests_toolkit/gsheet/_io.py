from typing import Dict
import toml
from shillelagh.backends.apsw.db import connect
import concurrent.futures
class IOArgument:
    def __init__(self,gcp_service_account:Dict, sheeturl:str):
        self.GCP = gcp_service_account
        self.sheeturl = sheeturl

    @classmethod
    def instantiate(cls,gcp_service_account:Dict, sheeturl:str):
        return cls(gcp_service_account,sheeturl)

    def to_dict(self) -> dict:
        ret = {}
        for key, value in self.__dict__.items():
            if hasattr(value, 'to_dict'):
                ret[key] = value.to_dict()
            else:
                ret[key] = value
        return ret
    @classmethod
    def fromSecretsTOML(cls,filepath:str = '.secrets.toml'):
        # 使用`toml`库加载和解析TOML文件
        with open(filepath, "r", encoding="utf-8") as toml_file:
            toml_data = toml.load(toml_file)

        gcp = toml_data['gcp_service_account']
        sheeturl = toml_data['private_gsheets_url']
        return cls.instantiate(gcp,sheeturl)


class GSheetIO:
    def __init__(self,io_args:IOArgument=None, enable_threading:bool = False):
        if io_args is None:
            self.args = IOArgument.fromSecretsTOML()
        else:
            self.args = io_args
        self.threading = enable_threading
        if self.threading:
            self.executor = concurrent.futures.ThreadPoolExecutor()
            self.executor.__enter__()
            self.running_tasks = []


    @classmethod
    def fromIOArgs(cls, io_args: IOArgument):
        return cls(io_args)

    def __login_to_google__(self):
        print("\n\n##########################\n\n")
        print("Login to Google API")

        connect_args = {
            "path": ":memory:",
            "adapters": "gsheetsapi",
            "adapter_kwargs": {
                "gsheetsapi": {
                    "service_account_info": {
                        **self.args.GCP
                    }
                }
            }
        }

        conn = connect(**connect_args)
        cursor = conn.cursor()
        print("Login done.")
        return cursor


    def run_query(self,query):
        '''

            Args:
                query: example: 'SELECT * FROM SHEET'. "SHEET" will be replaced by the gsheet url internally.

            Returns: query results

            '''
        cursor = self.__login_to_google__()
        sheet_url = self.args.sheeturl
        query = query.replace('SHEET', f'''"{sheet_url}"''')
        if not self.threading:
            return cursor.execute(query)
        else:
            def lazy(query):
                return cursor.execute(query)

            future = self.executor.submit(lazy,query)
            self.running_tasks.append(future)
            return future

    def sync(self, timeout:int=10) -> list:
        if self.threading:
            self.executor.__exit__(None,None,None)
            # Store futures and their corresponding index
            futures = {future: idx for idx, future in enumerate(self.running_tasks)}

            # Initialize an empty list of the same length as params
            ret = [None] * len(self.running_tasks)

            for future in concurrent.futures.as_completed(self.running_tasks):
                # Get the index of the completed future
                idx = futures[future]

                # Store the result at the appropriate index in ret
                try:
                    result = future.result(timeout)
                except concurrent.futures.TimeoutError:
                    result = None

                ret[idx] = result

            self.running_tasks.clear()
            return ret



    def get_whole_dataset(self):
        query = f'SELECT * FROM SHEET'
        dataset = self.run_query(query)
        return dataset

    def add_new_row(self,data: dict):
        columns_str = ", ".join(data.keys())
        new_values_str = ", ".join([f"\'{str(x)}\'" for x in data.values()])
        query = f'INSERT INTO SHEET ({columns_str}) VALUES ({new_values_str})'
        self.run_query(query)













