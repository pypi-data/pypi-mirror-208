import requests
import pandas as pd
from lxml import etree

def exchange_rate_cn() -> pd.DataFrame:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    }
    html = requests.get('https://www.waihui321.com/', headers=headers).text
    tmp = etree.HTML(html).xpath('//table[@class="boc"]//tr//text()')
    rates = []

    for i in range(0, len(tmp) - 7, 7):
        rates.append(tmp[i:i + 7])

    rates[0][1] = '代码'

    return pd.DataFrame(rates)

if __name__ == '__main__':
    print(exchange_rate_cn())
