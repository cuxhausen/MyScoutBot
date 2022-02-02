import requests
from bs4 import BeautifulSoup
import re


def get_khl(date):
    url = f"https://news.sportbox.ru/stats/{date}"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/"
                  "webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    if soup.find('div', id='sport_2').find('div', class_='b-online__tour-title') \
            .find('a', href=re.compile('/Vidy_sporta/Hokkej/KHL/stats')) is not None:
        data = soup.find('div', id='sport_2').find('div', class_='b-onlines-box') \
            .find_all('a', class_='b-onlines-box__item')
        for i in data:
            if i.find('div', class_='b-onlines-box__comment') is not None:
                print(
                    f"{i.find('div', class_='b-onlines-box__side_left').text.strip()} "
                    f"{i.find('div', class_='count').text.strip()}"
                    f"({i.find('div', class_='b-onlines-box__comment').text.strip().lstrip('(').rstrip(')')})"
                    f" {i.find('div', class_='b-onlines-box__side_right').text.strip()}"
                )
            else:
                print(
                    f"{i.find('div', class_='b-onlines-box__side_left').text.strip()} "
                    f"{i.find('div', class_='count').text.strip()}"
                    f" {i.find('div', class_='b-onlines-box__side_right').text.strip()}"
                )
            print("#################################")
    else:
        print('В этот день нет матчей КХЛ')
    return


def get_number_last_draw():
    url = 'https://www.stoloto.ru/6x45/archive'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/"
                  "apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    #data = soup.find("div", id="content").find_all("div", class_="elem")
    data = soup.find("div", class_="data drawings_data").find_all("div", class_="elem")
    #s = data[0].find("div", class_="draw_date").text.strip()
    last_draw = int(data[0].find("div", class_="draw").text.strip())
    #r = data[0].find("span", class_="zone").text.strip()
    #print(s)
    #print(p, type(p))
    #print(r)
    return last_draw

url_1 = f'https://www.stoloto.ru/6x45/archive/{get_number_last_draw()}'
print(url_1)


def get_last_ten():
    url = 'https://www.stoloto.ru/6x45/archive'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    data = soup.find("div", id="content").find_all("div", class_="elem")
    z1 = data[0].find("span", class_="zone").find_all("b")
    print(
        f'Тираж №{data[0].find("div", class_="draw").text.strip()}'
        f' {data[0].find("div", class_="draw_date").text.strip()}\n'
        f'{z1[0].text.strip()}  {z1[1].text.strip()}  {z1[2].text.strip()}  '
        f'{z1[3].text.strip()}  {z1[4].text.strip()}  {z1[5].text.strip()}'
        )
    #s = data[0].find("div", class_="draw_date").text.strip()
    #p = data[0].find("div", class_="draw").text.strip()
    #r = data[0].find("span", class_="zone").text.strip()
p = get_last_ten()
print(p, type(p))