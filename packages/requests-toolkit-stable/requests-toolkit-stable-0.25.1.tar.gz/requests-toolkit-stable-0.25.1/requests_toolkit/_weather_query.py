import requests
from lxml import etree

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
}

def weather_query(city):
    html = requests.get(f'http://www.tianqi.com/{city.lower()}/', headers=headers).text

    time = etree.HTML(html).xpath('//dl[@class="weather_info"]//dd[@class="week"]//text()')[0].replace('\u3000',                                                                                                   ', ').strip()
    city = etree.HTML(html).xpath('//dl[@class="weather_info"]//dd[@class="name"]//text()')[0]
    weather = ', '.join(etree.HTML(html).xpath('//dl[@class="weather_info"]//dd[@class="weather"]//span//text()'))
    shidu = ', '.join(etree.HTML(html).xpath('//dl[@class="weather_info"]//dd[@class="shidu"]//text()'))
    kongqi = ', '.join(etree.HTML(html).xpath('//dl[@class="weather_info"]//dd[@class="kongqi"]//text()'))
    general_weather_info = f'{time}. {city}为{weather}, {shidu}, {kongqi}.'

    detailed_weather_info = ''
    for i in etree.HTML(html).xpath('//div[@class="mainWeather"]//ul[@class="raweather760"]//a/@title')[0:-1:2]:
        detailed_weather_info += i + '; '

    weather_info = f'''{general_weather_info}

    局部地区详细天气情况：
    {detailed_weather_info}'''

    return weather_info