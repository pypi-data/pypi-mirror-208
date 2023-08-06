import asyncio
from typing import List
import time
import json
import os
from lxml import etree
from tqdm import tqdm
import requests
import aiohttp
class AirQualityQuery:
    KEY = '550b1b06-665d-41f5-b606-c26d06646a20'
    ENDPOINT = '''http://api.airvisual.com/v2/'''
    PATH = '.CITIES.json'
    HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
}

    if os.path.exists(PATH):
        with open(PATH, 'r', encoding='UTF-8') as f:
            CITIES = json.load(f)
    else:
        CITIES = dict()

    @classmethod
    async def tasks(cls, tasks: tuple):
        await asyncio.gather(*tasks)

    @classmethod
    def __get__provinces__(cls,country: str) -> List[str]:
        url = cls.ENDPOINT + 'states?'
        tmp = requests.get(url,dict(
            country=country,
            key=cls.KEY
        )).json()

        response_state = tmp['status']
        while response_state != 'success':
            time.sleep(10)
            tmp = requests.get(url, dict(
                country=country,
                key=cls.KEY
            )).json()
            response_state = tmp['status']
        provinces = [x['state'] for x in tmp['data']]
        return provinces

    @classmethod
    def __get__cities_in_province__(cls,province: str, country: str) -> List[str]:
        url = cls.ENDPOINT + 'cities?'
        tmp = requests.get(url,dict(
            state = province,
            key=cls.KEY,
            country = country
        )).json()

        response_state = tmp['status']
        while response_state != 'success':
            time.sleep(10)
            tmp = requests.get(url, dict(
                state=province,
                key=cls.KEY,
                country=country
            )).json()
            response_state = tmp['status']

        cities = [x['city'] for x in tmp['data']]
        return cities

    @classmethod
    def __get_cities_in_country__(cls,country:str) -> List[str]:
        if country not in cls.CITIES:
            cls.CITIES[country] = dict()
            provinces = cls.__get__provinces__(country)  # [str]
            for i in tqdm(range(len(provinces))):
                province = provinces[i]
                cities = cls.__get__cities_in_province__(province, country)
                cls.CITIES[country][province] = cities

            with open(cls.PATH,'w') as f:
                f.write(json.dumps(cls.CITIES))

        return cls.CITIES[country]

    @classmethod
    def air_quality_by_country(cls, country: str):
        if country not in cls.CITIES:
            data = cls.__get_cities_in_country__(country)
        else:
            data = cls.CITIES[country]

        aqi_values = []

        for prov in data.keys():
            # for city in cities:
            #     html = requests.get(f'''{url}/{prov.lower()}/{city.lower()}''', headers=cls.HEADERS).text
            #     try:
            #         aqi = int(etree.HTML(html).xpath('//p[@class="aqi-value__value"]//text()')[0])
            #     except:
            #         continue
            #     aqi_values.append((city,prov, aqi))
            #     if return_frequency and len(aqi_values) % return_frequency ==0:
            #         aqi_values.sort(key=lambda x: x[2])
            #         yield aqi_values
            aqi_values += cls.air_quality_by_province_country(country,prov)
            aqi_values.sort(key=lambda x: x[2])
            yield aqi_values


        aqi_mean = sum([x[2] for x in aqi_values]) / len(aqi_values)
        aqi_values.append(('mean', country, aqi_mean))
        yield aqi_values

    @classmethod
    def air_quality_by_province_country(cls,country:str,province_:str):
        province = province_[0].upper()
        province += province_[1:]

        if country not in cls.CITIES:
            data = cls.__get_cities_in_country__(country)
        else:
            data = cls.CITIES[country]
        if province not in data.keys():
            raise RuntimeError('There is no such province in this country.')

        cities = data[province] # [str]
        url = f'''https://www.iqair.com/{country.lower()}/{province.lower()}'''
        aqi_values = []

        async def task(city:str):
            # html = requests.get(f'''{url}/{city.lower()}''', headers=cls.HEADERS).text
            async with aiohttp.ClientSession() as session:
                async with session.get(f'''{url}/{city.lower()}''', headers=cls.HEADERS) as response:
                    html = await response.text()
            try:
                aqi = int(etree.HTML(html).xpath('//p[@class="aqi-value__value"]//text()')[0])
            except:
                return
            aqi_values.append((city, province, aqi))
        asyncio.run(cls.tasks(tuple(task(city) for city in cities)))

        if len(aqi_values) == 0:
            return aqi_values
        aqi_values.sort(key=lambda x: x[2])
        aqi_mean = sum([x[2] for x in aqi_values])/len(aqi_values)
        aqi_values.append(('mean',province,aqi_mean))
        return aqi_values


if __name__ == '__main__':
    # print(AirQualityQuery.__get__provinces__('china'))
    generator = AirQualityQuery.air_quality_by_country('china')
    for i in generator:
        print(i)
        print()
    # print(AirQualityQuery.air_quality_by_province_country('china','fujian'))
    # print(AirQualityQuery.air_quality_by_country('china'))
