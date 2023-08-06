from typing import List
from ..asyncpy import HTTPLoop
from ._language import Language
from ._engine import Engine


class BaseTranslator:
    def __init__(self, source: Language, dest: Language):
        self.src = source
        self.dst = dest
        self.__loop__ = HTTPLoop()

    def __a_translate_one__(self, text: str):
        raise NotImplementedError()

    def translate_n(self, texts: List[str], callback: callable = None):
        self.__loop__.clear()
        for t in texts:
            self.__a_translate_one__(t)

        if callback:
            self.__loop__.yield_done(callback)
        else:
            return self.__post_process__(self.__loop__.wait_all_done())

    def print_all_engines(self):
        print(Engine.__members__)

    def translate(self, text: str):
        self.__loop__.clear()
        self.__a_translate_one__(text)
        return self.__post_process__(self.__loop__.wait_all_done())

    def __post_process__(self, results):
        raise NotImplementedError()


class OpenAI_Translator(BaseTranslator):
    def __init__(self, source: Language, dest: Language, API_key):
        super().__init__(source, dest)
        self.api_key = API_key

    def __a_translate_one__(self, text: str, ):
        self.__loop__.post(
            url='https://api.openai.com/v1/chat/completions',
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.api_key)
            },
            json=dict(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system',
                     'content': f"Please translate the following sentences into {self.dst}. Only send back the translated texts and keep the punctuation, the special char such as \"[\", \"]\" unchanged. The source sentence is: "},
                    {"role": "user", "content": text},
                ],
                temperature=0
            )
        )

    def __post_process__(self, results):
        return [i['choices'][0]['message']['content'] for i in results]
