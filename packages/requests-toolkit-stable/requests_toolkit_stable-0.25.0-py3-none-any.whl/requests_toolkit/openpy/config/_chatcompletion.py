from typing import Union, List


class ChatCompletionConfig:
    def __init__(self,*,
        user_msg: str,
        user_name: str = None,
        assistant: str = None,
        local_system:str = None,
        temperature:float = 1,
        top_p:float = 1,
        n:int = 1,
        stream:bool = False,
        stop: Union[str, List[str]] = None,
        max_tokens:int = 1000,
        presence_penalty:float = 0,
        frequency_penalty:float = 0,
        only_response = True,
                 ):
        '''

         :param user_msg: user message
         :param assistant: external knowledge base. E.g. chat history
         :param temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the     output more random, while lower values like 0.2 will make it more focused and deterministic.
             We generally recommend altering this or top_p but not both.
         :param top_p: An alternative to sampling with temperature, called nucleus sampling, where the model         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising    the top 10% probability mass are considered.
             We generally recommend altering this or temperature but not both.
         :param n: How many chat completion choices to generate for each input message.
         :param stream: If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message.
         :param stop: Up to 4 sequences where the API will stop generating further tokens.
         :param max_tokens: The maximum number of tokens allowed for the generated answer. By default, the number of tokens the model can return will be (4096 - prompt tokens).
         :param presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
         :param frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
         :param user_name: A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. Learn more.
         :param only_response: if only return the text response from ChatGPT

         :return:
         '''
        self.user_name = user_name
        self.user_msg = user_msg
        self.assistant = assistant
        self.local_system =  local_system
        self.temparature = temperature
        self.top_p = top_p
        self.n = n
        self.stream = stream
        self.stop = stop
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.only_response = only_response

    def to_dict(self) -> dict:
        ret = {}
        for key, value in self.__dict__.items():
            if hasattr(value, 'to_dict'):
                ret[key] = value.to_dict()
            else:
                ret[key] = value
        return ret