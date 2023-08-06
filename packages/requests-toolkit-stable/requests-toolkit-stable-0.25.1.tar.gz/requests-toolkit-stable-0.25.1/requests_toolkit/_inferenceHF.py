import json
import requests
from typing import Union, List


class HFBot:
    API_URL = "https://api-inference.huggingface.co/models/"
    
    def __init__(self, API_key:str) -> None:
        self.apikey = API_key
        self.headers = {"Authorization": f"Bearer {self.apikey}"}


    def inference(self, inputs: Union[List[str], str], model_name: str) -> dict:
        payload = dict(
            inputs=inputs,
            options=dict(
                wait_for_model=True
            )
        )

        data = json.dumps(payload)
        response = requests.request(
            "POST", self.API_URL+model_name, headers=self.headers, data=data)
        return json.loads(response.content.decode("utf-8"))


if __name__ == '__main__':
    bot = HFBot('apikey')
    print(bot.inference(
        inputs='hi how are you?',
        model_name='t5-small'
    ))
