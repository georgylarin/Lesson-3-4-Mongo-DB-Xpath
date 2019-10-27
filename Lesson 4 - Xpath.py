### Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru.
# Для парсинга использовать xpath. Структура данных должна содержать:
# * название источника,
# * наименование новости,
# * ссылку на новость,
# * дата публикации

import requests
from lxml import html
from pprint import pprint
import pandas as pd
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}

list_data_source = []
list_news_link = []
list_public_date = []
list_news_text = []

# Подборка из lenta.ru

link = 'https://m.lenta.ru'
request = requests.get(link, headers=headers)
root = html.fromstring(request.text)

result_list = root.xpath('//li[@class="b-list-item b-list-item_news"]//a[starts-with(@href, "/news")]')
month_dict = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
          'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}

for i in result_list:
    data_source = 'lenta.ru'
    list_data_source.append(data_source)

    try:
        news_link = 'https://lenta.ru' + i.xpath('./@href')[0]
    except Exception as e:
        print(str(i) + ': '+ str(e))
        news_link = None
    list_news_link.append(news_link)

    try:
        news_text = i.xpath('./span[@class="b-list-item__title"]/text()')[0]
    except Exception as e:
        print(news_link + ': '+ str(e))
        news_text = None
    list_news_text.append(news_text)

    try:
        public_data_string = i.xpath('./span/time/@title')[0]
        date = public_data_string.split()
        public_date = datetime.date(int(date[2])), month_dict.get(date[1], int(date[0]))
    except Exception as e:
        link = news_link
        request = requests.get(link, headers=headers)
        root = html.fromstring(request.text)
        public_date = root.xpath('//div[@class ="b-topic__info"]/time[@ class ="g-date"]/@datetime')[0].split('T')[0]
    list_public_date.append(public_date)

news_lenta = pd.DataFrame({'data_source': list_data_source,
                           'news_link': list_news_link,
                           'news_text': list_news_text,
                           'public_date': list_public_date})

pprint(news_lenta.head(5))

# Подборка из mail.ru

link = 'https://mail.ru/?from=m'
request = requests.get(link, headers=headers)
root = html.fromstring(request.text)

result_list = root.xpath('//a[@class="list__item"]')

for i in result_list:
    data_source = 'mail.ru'
    list_data_source.append(data_source)

    try:
        news_link = i.xpath('./@href')[0]
    except Exception as e:
        print(str(i) + ': ' + str(e))
        news_link = None
    list_news_link.append(news_link)

    try:
        news_text = i.xpath('./div/span/text()')[0].replace('\xa0', '')
    except Exception as e:
        print(news_link + ': ' + str(e))
        news_text = None
    list_news_text.append(news_text)

    link = news_link
    request = requests.get(link, headers=headers)
    root = html.fromstring(request.text)
    try:
        public_date = root.xpath('//span[@class="note__text breadcrumbs__text js-ago"]/''@datetime\
                                 |//time[@class="note__text breadcrumbs__text js-ago"]/@datetime')[0].split('T')[0]
    except Exception as e:
        print(news_link + ': ' + str(e))
        public_date = None
    list_public_date.append(public_date)

news_mail = pd.DataFrame({'data_source': list_data_source,
                           'news_link': list_news_link,
                           'news_text': list_news_text,
                           'public_date': list_public_date})
pprint(news_mail.head(6))

