import pandas as pd
import requests
from lxml import etree

def process_one_url(url:str) -> list:
    html = requests.get(url).text
    li = list(etree.HTML(html).xpath("//p//text()"))
    li = list(filter(lambda x: len(x.split(" ")) > 50, li))
    li = [x[1:].replace('\n', ' ') for x in li]
    return li

def query_abstracts_arxiv(urls: list) ->pd.DataFrame:
    ret = []
    for url in urls:
        ret.extend(process_one_url(url))
    df = pd.DataFrame(ret)
    return df

