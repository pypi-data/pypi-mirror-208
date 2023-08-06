import requests
import re
from pprint import pprint as pp


class YTBInfoBot:
    def __init__(self, urls: list):
        self.database = {
            'https://www.youtube.com/c/TechWithTim/videos': None
        }
        self.headers = {
            'cookie': 'VISITOR_INFO1_LIVE=9qZVrzB27uI; PREF=f4=4000000&tz=Asia.Shanghai; _ga=GA1.2.621834420.1648121145; _gcl_au=1.1.1853038046.1648121145; NID=511=Zc1APdmEbCD-iqVNVgI_vD_0S3LVI3XSfl-wUZEvvMU2MLePFKsQCaKUlUtchHSg-kWEVMGOhWUbxpQMwHeIuLjhxaslwniMh1OsjVfmOeTfhpwcRYpMgqpZtNQ7qQApY21xEObCvIez6DCMbjRhRQ5P7siOD3X87QX0CFyUxmY; OTZ=6430350_24_24__24_; GPS=1; YSC=0E115KqM_-I; GOOGLE_ABUSE_EXEMPTION=ID=d02004902c3d0f4d:TM=1648620854:C=r:IP=47.57.243.77-:S=YmZXPW7dxbu83bDuauEpXpE; CONSISTENCY=AGDxDeNysJ2boEmzRP4v6cwgg4NsdN4-FYQKHCGhA0AeW1QjFIU1Ejq1j8l6lwAc6c-pYTJiSaQItZ1M6QeI1pQ3wictnWXTOZ6_y8EKlt0Y_JdakwW6srR39-NLuPgSgXrXwtS0XTUGXpdnt4k3JjQ',
            'referer': 'https://www.youtube.com/results?search_query=jk%E7%BE%8E%E5%A5%B3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'

        }

        for url in urls:
            self.database[url] = None
        self.setup()

    def setup(self):
        for url in self.database.keys():
            self.database[url] = self.latest_video_title(url)

    def latest_video_title(self, url):
        html = requests.get(url, headers=self.headers).text
        result = re.findall('''"title":{"runs":[{"text":"[a-zA-Z -_0-9:]*''', html)
        result = result[0]
        index = result.rfind('"', 0, len(result) - 1)
        title = result[index + 1:-1]
        return title

    def print_database(self):
        pp(self.database)


