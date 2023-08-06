import requests
from lxml import etree

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
}

def thesis_info(**kwargs):
    if 'urls' in kwargs:
        urls = kwargs['urls']
    else:
        urls = urls = [
            'https://wwwmatthes.in.tum.de/pages/kr45xfyxvcda/Anum-Afzal',
            'https://wwwmatthes.in.tum.de/pages/zvs4gw49ru7f/Phillip-Schneider',
            'https://wwwmatthes.in.tum.de/pages/1ejjrtvitero5/Stephen-Meisenbacher',
            'https://wwwmatthes.in.tum.de/pages/1n0vb1ew7e6u5/Tim-Schopf',
            ]

    result = ''

    for i in urls:
        html = requests.get(i,headers=headers).text
        content = ', '.join(etree.HTML(html).xpath('//span[@style]//text()')).strip()
        result += f'link: {i}, content: {content}'
        result += '\n'

    return result

