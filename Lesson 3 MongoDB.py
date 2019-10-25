### Задание №1 Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую
### собранные вакансии в созданную БД

from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['VACANCY']
vac = db.vac

# Повторяем скрипт из домашнего задания №2
superjob = []
hh = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
main_link1 = 'https://www.superjob.ru'
main_link2 = 'https://hh.ru'

vacancy = input('Какая вакансия вас интересует?  ')
pages = 3

def hh_get():
    html = requests.get(main_link2 + '/search/vacancy?st=searchVacancy&text=' + vacancy, headers=headers).text
    for i in range(pages):
        parsed_html = bs(html, 'lxml')
        vacancy_list = parsed_html.findAll('div', {'class': 'vacancy-serp-item'})

        for vac in vacancy_list:
            hh_data = {}
            vac_info = vac.find("span", {'class': 'g-user-content'}).findChild()
            vacancy_name = vac_info.getText()
            vacancy_link = vac_info['href']
            vacancy_salary = vac.find('div', {'class': 'vacancy-serp-item__compensation'})
            if not vacancy_salary:
                salary = {'min': 0, 'max': 0, 'type': 'Не указано'}
            else:
                salary_data = re.findall('(\d+[\s\d]*)', vacancy_salary.getText())
                salary_type = re.findall('([А-яA-z]{3}\.*)', vacancy_salary.getText())
                if not salary_type:
                    salary_type = 'руб.'
                if len(salary_data) > 1:
                    salary = {'min': int(salary_data[0].replace('\xa0', '')),
                                'max': int(salary_data[1].replace('\xa0', '')), 'type': salary_type[0]}
                else:
                    salary = {'min': int(salary_data[0].replace('\xa0', '')), 'max': 0, 'type': salary_type[0]}

            company = vac.find('div', {'class': 'vacancy-serp-item__meta-info'}).findChild()
            if not company:
                company = 'Не указано'
            else:
                company = company.getText()

            # Собираем и складываем
            hh_data['vacancy_name'] = vacancy_name
            hh_data['company'] = company
            hh_data['salary'] = salary
            hh_data['vacancy_link'] = vacancy_link
            hh.append(hh_data)

        # получаем ссылку на следующую страницу
        link_next = parsed_html.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        if not link_next:
            print(f'На сайте "{main_link2}" доступно лишь {i + 1} страниц(ы) информации из желаемых {pages}\n')
            break
        else:
            link_next = link_next['href']
            new_link = main_link2 + link_next
            html = requests.get(new_link, headers=headers).text

    return hh


pd.set_option('display.max_columns', None)
data_hh = pd.DataFrame(hh_get())
print(f'На сайте {main_link2} всего найдено {len(hh)} вакансий по слову "{vacancy}"')
# print(data_hh.head(5))

def superjob_get():
    html1 = requests.get(main_link1 + '/vacancy/search/?keywords=' + vacancy, headers=headers).text

    for i in range(3):
        parsed_html = bs(html1, 'lxml')
        vacancy_list = parsed_html.findAll('div', {'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})

        for vac in vacancy_list:
            superjob_data = {}
            main_info = vac.find('div', {'class': '_2g1F-'}).findChild()

            vacancy_name = main_info.find('div', {'_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).getText()

            vacancy_link = main_link1 + main_info.find('a')['href']

            vacancy_salary = main_info.find('span',
                                            {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})

            if not vacancy_salary:
                salary = {'min': 0, 'max': 0, 'type': 'Не указано'}
            else:
                salary_data = re.findall('(\d+[\s\d]*)', vacancy_salary.getText())
                if not salary_data:
                    salary = {'min': 0, 'max': 0, 'type': 'не указан'}
                else:
                    if len(salary_data) > 1:
                        salary = {'min': int(salary_data[0].replace('\xa0', '')),
                                  'max': int(salary_data[1].replace('\xa0', '')), 'type': 'руб.'}
                    else:
                        salary = {'min': int(salary_data[0].replace('\xa0', '')), 'max': 0, 'type': 'руб.'}

            company = main_info.find('span', {'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _3e53o _15msI'})
            if not company:
                company = 'Не указано'
            else:
                company = company.getText()

            # Собираем и складываем
            superjob_data['vacancy_name'] = vacancy_name
            superjob_data['company'] = company
            superjob_data['salary'] = salary
            superjob_data['vacancy_link'] = vacancy_link
            superjob.append(superjob_data)

        # получаем ссылку на следующую страницу
        link_next = parsed_html.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe'})
        if not link_next:
            if i + 1 < pages:
                print(f'На сайте "{main_link2}" доступно лишь {i + 1} страниц(ы) информации из желаемых {pages}\n')
            break
        else:
            link_next = link_next['href']
            new_link = main_link2 + link_next
            html = requests.get(new_link, headers=headers).text
    return superjob


data_superjob = pd.DataFrame(superjob_get())

print(f'На сайте {main_link1} всего найдено {len(superjob)} вакансий по слову "{vacancy}"')

# print(data_superjob.head(5))

### функция для сохранения в базу

def to_mongodb(items):
    try:
        dubl = 0
        unic = 0
        for data in items:
            link1 = data['vacancy_link']
            x = 0
            objects = vac.find()
            for obj in objects:
                link2 = obj['vacancy_link']
                if link1 == link2:
                    x = 1
                    dubl +=1
            if x == 0:
                vac.insert_one(data)
                unic += 1
        if unic == 0:
            res = 'новых вакансий не обнаружено'
        else:
            res = f'записано {unic} новых вакансий, {dubl} - уже существуют в базе .'
    except:
        res = 'возникли проблемы при сохранении в MongoDB.\n'
    return res

# Получаем данные
hh_data = hh_get()
superjob_data = superjob_get()

print("=" * 60 + 'Создание БД на MongoDB' + "=" * 75)

# Сохраняем в базу MongoDB "VACANCY"
res = to_mongodb(hh_data)
print(f'При обработке данных hh.ru {res}')
res = to_mongodb(superjob_data)
print(f'При обработке данных superjob.ru {res}')

# Задание №2 Выводим вакансии из базы "VACANCY" по нужному уровню зарплаты

num = int(input('\nКакой уровень зарплаты вас интересует (рублей)?: '))

def zapros(num):
    objects = vac.find({['salary']['min']: {'$gte': num}}, {'vacancy_name', 'salary', 'vacancy_link'})
    for o in objects:
        pprint(f"<{o['vacancy_name']}> <{o['vacancy_link']}> зарплата {o['salary']['min']} {o['salary']['type']}")

zapros(num)

# Другой вариант, который у меня тоже не пошёл:

# objects = vac.find()
# for o in objects:
#     if (o['salary']['max']  num) or (o['salary']['min'] != 0 and o['salary']['max'] == 0):
#         if o['salary']['max'] != 0:
#             s_max = f" до {o['salary']['max']}"
#         else:
#             s_max = ''
#         print(f"{o['vacancy_name']}, зарплата от {o['salary']['min']}{s_max}, ссылка: {o['vacancy_link']}")

