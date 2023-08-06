import requests
from lxml import etree

class RealPythonNews:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    }

    ENDPOINT = 'https://realpython.com'

    @classmethod
    def all(cls, return_links=False):
        '''
        return all news titles and additionally the links if return_links = True
        '''
        html = requests.get(cls.ENDPOINT + '/tutorials/community', headers=cls.headers).text
        titles = etree.HTML(html).xpath('//h2[@class="card-title h4 my-0 py-0"]//text()')
        if return_links:
            hrefs = etree.HTML(html).xpath('//a[@class=" "]/@href')
            hrefs = [cls.ENDPOINT + x for x in hrefs]
            return titles,hrefs
        return titles

    @classmethod
    def latests(cls, return_links = False):
        if return_links:
            tmp = cls.all(return_links)
            return tmp[0][0], tmp[1][0]
        else:
            return cls.all()[0]




if __name__ == '__main__':
    print(RealPythonNews.latests(True))
    print(RealPythonNews.latests())

