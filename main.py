import requests
import datetime
from config import tg_bot_token, open_weather_token, currencylayer_token, exchange_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
from aiogram.utils import executor
from bs4 import BeautifulSoup
import re


bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Курсы валют", "Погода", "Результаты КХЛ", "Результаты лотерей", "Учить английский"]
    keyboard.add(*buttons)
    await message.reply("Привет! Я бот MyScout. Моя задача помогать тебе!\nНадеюсь буду полезен!\nВыбери опцию ниже ↓",
                        reply_markup=keyboard
                        )


@dp.message_handler(lambda message: message.text == "Курсы валют")
async def get_data_currencies(message: types.Message):
    try:
        req_btc = requests.get("https://yobit.net/api/3/ticker/btc_usd")
        res_btc = req_btc.json()
        sell_price_btc = res_btc["btc_usd"]["sell"]

        req_rub_usd = requests.get(f"http://api.currencylayer.com/live?access_key={currencylayer_token}")
        res_rub_usd = req_rub_usd.json()
        price_rub_usd = res_rub_usd["quotes"]["USDRUB"]

        req_rub_eur = requests.get(f"http://api.exchangeratesapi.io/v1/latest?access_key={exchange_token}")
        res_rub_eur = req_rub_eur.json()
        price_rub_eur = res_rub_eur["rates"]["RUB"]

        await message.reply(
            f"***{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}***\n"
            f"Курс доллара: 1$ = {round(price_rub_usd, 2)} руб.\n"
            f"Курс евро: 1€ = {round(price_rub_eur, 2)} руб.\nКурс биткоина: 1₿ = {round(sell_price_btc, 2)}$\n"
            f"***Хорошего дня!***"
            )
    except Exception as ex:
        print(ex)
        await message.reply("Эээм...Что-то пошло не так...")

"""

@dp.message_handler(lambda message: message.text == "Погода")
async def get_weather(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Артын", "Омск", "Новосибирск", "Москва", "Санкт-Петербург", "Казань"]
    keyboard.add(*buttons)
    await message.reply("Выбери город",
                        reply_markup=keyboard,
                        )
    await message.reply("Введи название города...")
"""


@dp.message_handler(lambda message: message.text == "Погода")
async def get_weather(message: types.Message):
    await message.reply("Введи название города...")


@dp.message_handler(lambda message: message.text == "Результаты КХЛ")
async def get_khl_results(message: types.Message):
    buttons =[
        types.InlineKeyboardButton(text="Навигационный календарь", callback_data="navigation_calendar"),
        types.InlineKeyboardButton(text="Диалоговый календарь", callback_data="dialog_calendar")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Укажи дату! А для этого выбери календарь ↓", reply_markup=keyboard)


@dp.callback_query_handler(text="navigation_calendar")
async def nav_cal_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           "Выбери дату: ",
                           reply_markup=await SimpleCalendar().start_calendar()
                           )


@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, date.strftime("%Y-%m-%d"))
        await bot.send_message(callback_query.from_user.id, callback_data)


@dp.callback_query_handler(text="dialog_calendar")
async def simple_cal_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           "Выбери дату: ",
                           reply_markup=await DialogCalendar().start_calendar()
                           )


@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, date.strftime("%Y-%m-%d"))
        await bot.send_message(callback_query.from_user.id, callback_data)


@dp.callback_query_handler(lambda c: c.data.startswith('20'))
async def send_khl_results(callback_query: types.CallbackQuery):
    url = f'https://news.sportbox.ru/stats/2022-01-06'
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
                await bot.answer_callback_query(callback_query.id)
                await bot.send_message(callback_query.from_user.id,
                                       f"{i.find('div', class_='b-onlines-box__side_left').text.strip()} "
                                       f"{i.find('div', class_='count').text.strip()}"
                                       f"({i.find('div', class_='b-onlines-box__comment').text.strip().lstrip('(').rstrip(')')})"
                                       f" {i.find('div', class_='b-onlines-box__side_right').text.strip()}"
                                       )
            else:
                await bot.answer_callback_query(callback_query.id)
                await bot.send_message(callback_query.from_user.id,
                                       f"{i.find('div', class_='b-onlines-box__side_left').text.strip()} "
                                       f"{i.find('div', class_='count').text.strip()}"
                                       f" {i.find('div', class_='b-onlines-box__side_right').text.strip()}"
                                       )
        await bot.send_message(callback_query.from_user.id,
                               f"Надеюсь результаты не испортили настроение!\n"
                               f"****Хорошего дня!****"
                               )
    else:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Сегодня нет матчей")


@dp.message_handler(lambda message: message.text == "Результаты лотерей")
async def get_draw_results(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="6 из 45 (десять последних)", callback_data="6_45_results"),
        types.InlineKeyboardButton(text="6 из 36 (десять последних)", callback_data="6_36_results"),
        types.InlineKeyboardButton(text="7 из 49 (десять последних)", callback_data="7_49_results")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Думаю, что делать дальше, понятно", reply_markup=keyboard)


@dp.callback_query_handler(text="6_45_results")
async def get_draw_6_45(callback_query: types.CallbackQuery):
    url = "https://www.stoloto.ru/6x45/archive"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/"
                  "apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    data = soup.find("div", id="content").find_all("div", class_="elem")
    z1 = data[0].find("span", class_="zone").find_all("b")
    z2 = data[1].find("span", class_="zone").find_all("b")
    z3 = data[2].find("span", class_="zone").find_all("b")
    z4 = data[3].find("span", class_="zone").find_all("b")
    z5 = data[4].find("span", class_="zone").find_all("b")
    z6 = data[5].find("span", class_="zone").find_all("b")
    z7 = data[6].find("span", class_="zone").find_all("b")
    z8 = data[7].find("span", class_="zone").find_all("b")
    z9 = data[8].find("span", class_="zone").find_all("b")
    z10 = data[9].find("span", class_="zone").find_all("b")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           f'Тираж №{data[0].find("div", class_="draw").text.strip()} '
                           f'от {data[0].find("div", class_="draw_date").text.strip()}\n'
                           f'{z1[0].text.strip()}  {z1[1].text.strip()}  {z1[2].text.strip()}  '
                           f'{z1[3].text.strip()}  {z1[4].text.strip()}  {z1[5].text.strip()}\n'
                           f'Тираж №{data[1].find("div", class_="draw").text.strip()} '
                           f'от {data[1].find("div", class_="draw_date").text.strip()}\n'
                           f'{z2[0].text.strip()}  {z2[1].text.strip()}  {z2[2].text.strip()}  '
                           f'{z2[3].text.strip()}  {z2[4].text.strip()}  {z2[5].text.strip()}\n'
                           f'Тираж №{data[2].find("div", class_="draw").text.strip()} '
                           f'от {data[2].find("div", class_="draw_date").text.strip()}\n'
                           f'{z3[0].text.strip()}  {z3[1].text.strip()}  {z3[2].text.strip()}  '
                           f'{z3[3].text.strip()}  {z3[4].text.strip()}  {z3[5].text.strip()}\n'
                           f'Тираж №{data[3].find("div", class_="draw").text.strip()} '
                           f'от {data[3].find("div", class_="draw_date").text.strip()}\n'
                           f'{z4[0].text.strip()}  {z4[1].text.strip()}  {z4[2].text.strip()}  '
                           f'{z4[3].text.strip()}  {z4[4].text.strip()}  {z4[5].text.strip()}\n'
                           f'Тираж №{data[4].find("div", class_="draw").text.strip()} '
                           f'от {data[4].find("div", class_="draw_date").text.strip()}\n'
                           f'{z5[0].text.strip()}  {z5[1].text.strip()}  {z5[2].text.strip()}  '
                           f'{z5[3].text.strip()}  {z5[4].text.strip()}  {z5[5].text.strip()}\n'
                           f'Тираж №{data[5].find("div", class_="draw").text.strip()} '
                           f'от {data[5].find("div", class_="draw_date").text.strip()}\n'
                           f'{z6[0].text.strip()}  {z6[1].text.strip()}  {z6[2].text.strip()}  '
                           f'{z6[3].text.strip()}  {z6[4].text.strip()}  {z6[5].text.strip()}\n'
                           f'Тираж №{data[6].find("div", class_="draw").text.strip()} '
                           f'от {data[6].find("div", class_="draw_date").text.strip()}\n'
                           f'{z7[0].text.strip()}  {z7[1].text.strip()}  {z7[2].text.strip()}  '
                           f'{z7[3].text.strip()}  {z7[4].text.strip()}  {z7[5].text.strip()}\n'
                           f'Тираж №{data[7].find("div", class_="draw").text.strip()} '
                           f'от {data[7].find("div", class_="draw_date").text.strip()}\n'
                           f'{z8[0].text.strip()}  {z8[1].text.strip()}  {z8[2].text.strip()}  '
                           f'{z8[3].text.strip()}  {z8[4].text.strip()}  {z8[5].text.strip()}\n'
                           f'Тираж №{data[8].find("div", class_="draw").text.strip()} '
                           f'от {data[8].find("div", class_="draw_date").text.strip()}\n'
                           f'{z9[0].text.strip()}  {z9[1].text.strip()}  {z9[2].text.strip()}  '
                           f'{z9[3].text.strip()}  {z9[4].text.strip()}  {z9[5].text.strip()}\n'
                           f'Тираж №{data[9].find("div", class_="draw").text.strip()} '
                           f'от {data[9].find("div", class_="draw_date").text.strip()}\n'
                           f'{z10[0].text.strip()}  {z10[1].text.strip()}  {z10[2].text.strip()}  '
                           f'{z10[3].text.strip()}  {z10[4].text.strip()}  {z10[5].text.strip()}\n'
                           )


@dp.callback_query_handler(text="6_36_results")
async def get_draw_6_36(callback_query: types.CallbackQuery):
    url = "https://www.stoloto.ru/6x36/archive"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/"
                  "apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    data = soup.find("div", id="content").find_all("div", class_="elem")
    z1 = data[0].find("span", class_="zone").find_all("b")
    z2 = data[1].find("span", class_="zone").find_all("b")
    z3 = data[2].find("span", class_="zone").find_all("b")
    z4 = data[3].find("span", class_="zone").find_all("b")
    z5 = data[4].find("span", class_="zone").find_all("b")
    z6 = data[5].find("span", class_="zone").find_all("b")
    z7 = data[6].find("span", class_="zone").find_all("b")
    z8 = data[7].find("span", class_="zone").find_all("b")
    z9 = data[8].find("span", class_="zone").find_all("b")
    z10 = data[9].find("span", class_="zone").find_all("b")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           f'Тираж №{data[0].find("div", class_="draw").text.strip()} '
                           f'от {data[0].find("div", class_="draw_date").text.strip()}\n'
                           f'{z1[0].text.strip()}  {z1[1].text.strip()}  {z1[2].text.strip()}  '
                           f'{z1[3].text.strip()}  {z1[4].text.strip()}  {z1[5].text.strip()}\n'
                           f'Тираж №{data[1].find("div", class_="draw").text.strip()} '
                           f'от {data[1].find("div", class_="draw_date").text.strip()}\n'
                           f'{z2[0].text.strip()}  {z2[1].text.strip()}  {z2[2].text.strip()}  '
                           f'{z2[3].text.strip()}  {z2[4].text.strip()}  {z2[5].text.strip()}\n'
                           f'Тираж №{data[2].find("div", class_="draw").text.strip()} '
                           f'от {data[2].find("div", class_="draw_date").text.strip()}\n'
                           f'{z3[0].text.strip()}  {z3[1].text.strip()}  {z3[2].text.strip()}  '
                           f'{z3[3].text.strip()}  {z3[4].text.strip()}  {z3[5].text.strip()}\n'
                           f'Тираж №{data[3].find("div", class_="draw").text.strip()} '
                           f'от {data[3].find("div", class_="draw_date").text.strip()}\n'
                           f'{z4[0].text.strip()}  {z4[1].text.strip()}  {z4[2].text.strip()}  '
                           f'{z4[3].text.strip()}  {z4[4].text.strip()}  {z4[5].text.strip()}\n'
                           f'Тираж №{data[4].find("div", class_="draw").text.strip()} '
                           f'от {data[4].find("div", class_="draw_date").text.strip()}\n'
                           f'{z5[0].text.strip()}  {z5[1].text.strip()}  {z5[2].text.strip()}  '
                           f'{z5[3].text.strip()}  {z5[4].text.strip()}  {z5[5].text.strip()}\n'
                           f'Тираж №{data[5].find("div", class_="draw").text.strip()} '
                           f'от {data[5].find("div", class_="draw_date").text.strip()}\n'
                           f'{z6[0].text.strip()}  {z6[1].text.strip()}  {z6[2].text.strip()}  '
                           f'{z6[3].text.strip()}  {z6[4].text.strip()}  {z6[5].text.strip()}\n'
                           f'Тираж №{data[6].find("div", class_="draw").text.strip()} '
                           f'от {data[6].find("div", class_="draw_date").text.strip()}\n'
                           f'{z7[0].text.strip()}  {z7[1].text.strip()}  {z7[2].text.strip()}  '
                           f'{z7[3].text.strip()}  {z7[4].text.strip()}  {z7[5].text.strip()}\n'
                           f'Тираж №{data[7].find("div", class_="draw").text.strip()} '
                           f'от {data[7].find("div", class_="draw_date").text.strip()}\n'
                           f'{z8[0].text.strip()}  {z8[1].text.strip()}  {z8[2].text.strip()}  '
                           f'{z8[3].text.strip()}  {z8[4].text.strip()}  {z8[5].text.strip()}\n'
                           f'Тираж №{data[8].find("div", class_="draw").text.strip()} '
                           f'от {data[8].find("div", class_="draw_date").text.strip()}\n'
                           f'{z9[0].text.strip()}  {z9[1].text.strip()}  {z9[2].text.strip()}  '
                           f'{z9[3].text.strip()}  {z9[4].text.strip()}  {z9[5].text.strip()}\n'
                           f'Тираж №{data[9].find("div", class_="draw").text.strip()} '
                           f'от {data[9].find("div", class_="draw_date").text.strip()}\n'
                           f'{z10[0].text.strip()}  {z10[1].text.strip()}  {z10[2].text.strip()}  '
                           f'{z10[3].text.strip()}  {z10[4].text.strip()}  {z10[5].text.strip()}\n'
                           )


@dp.callback_query_handler(text="7_49_results")
async def get_draw_7_49(callback_query: types.CallbackQuery):
    url = "https://www.stoloto.ru/7x49/archive"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/"
                  "apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "96.0.4664.110 YaBrowser/22.1.0.2517 Yowser/2.5 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    data = soup.find("div", id="content").find_all("div", class_="elem")
    z1 = data[0].find("span", class_="zone").find_all("b")
    z2 = data[1].find("span", class_="zone").find_all("b")
    z3 = data[2].find("span", class_="zone").find_all("b")
    z4 = data[3].find("span", class_="zone").find_all("b")
    z5 = data[4].find("span", class_="zone").find_all("b")
    z6 = data[5].find("span", class_="zone").find_all("b")
    z7 = data[6].find("span", class_="zone").find_all("b")
    z8 = data[7].find("span", class_="zone").find_all("b")
    z9 = data[8].find("span", class_="zone").find_all("b")
    z10 = data[9].find("span", class_="zone").find_all("b")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           f'Тираж №{data[0].find("div", class_="draw").text.strip()} '
                           f'от {data[0].find("div", class_="draw_date").text.strip()}\n'
                           f'{z1[0].text.strip()}  {z1[1].text.strip()}  {z1[2].text.strip()}  '
                           f'{z1[3].text.strip()}  {z1[4].text.strip()}  {z1[5].text.strip()}  {z1[6].text.strip()}\n'
                           f'Тираж №{data[1].find("div", class_="draw").text.strip()} '
                           f'от {data[1].find("div", class_="draw_date").text.strip()}\n'
                           f'{z2[0].text.strip()}  {z2[1].text.strip()}  {z2[2].text.strip()}  '
                           f'{z2[3].text.strip()}  {z2[4].text.strip()}  {z2[5].text.strip()}  {z2[6].text.strip()}\n'
                           f'Тираж №{data[2].find("div", class_="draw").text.strip()} '
                           f'от {data[2].find("div", class_="draw_date").text.strip()}\n'
                           f'{z3[0].text.strip()}  {z3[1].text.strip()}  {z3[2].text.strip()}  '
                           f'{z3[3].text.strip()}  {z3[4].text.strip()}  {z3[5].text.strip()}  {z3[6].text.strip()}\n'
                           f'Тираж №{data[3].find("div", class_="draw").text.strip()} '
                           f'от {data[3].find("div", class_="draw_date").text.strip()}\n'
                           f'{z4[0].text.strip()}  {z4[1].text.strip()}  {z4[2].text.strip()}  '
                           f'{z4[3].text.strip()}  {z4[4].text.strip()}  {z4[5].text.strip()}  {z4[6].text.strip()}\n'
                           f'Тираж №{data[4].find("div", class_="draw").text.strip()} '
                           f'от {data[4].find("div", class_="draw_date").text.strip()}\n'
                           f'{z5[0].text.strip()}  {z5[1].text.strip()}  {z5[2].text.strip()}  '
                           f'{z5[3].text.strip()}  {z5[4].text.strip()}  {z5[5].text.strip()}  {z5[6].text.strip()}\n'
                           f'Тираж №{data[5].find("div", class_="draw").text.strip()} '
                           f'от {data[5].find("div", class_="draw_date").text.strip()}\n'
                           f'{z6[0].text.strip()}  {z6[1].text.strip()}  {z6[2].text.strip()}  '
                           f'{z6[3].text.strip()}  {z6[4].text.strip()}  {z6[5].text.strip()}  {z6[6].text.strip()}\n'
                           f'Тираж №{data[6].find("div", class_="draw").text.strip()} '
                           f'от {data[6].find("div", class_="draw_date").text.strip()}\n'
                           f'{z7[0].text.strip()}  {z7[1].text.strip()}  {z7[2].text.strip()}  '
                           f'{z7[3].text.strip()}  {z7[4].text.strip()}  {z7[5].text.strip()}  {z7[6].text.strip()}\n'
                           f'Тираж №{data[7].find("div", class_="draw").text.strip()} '
                           f'от {data[7].find("div", class_="draw_date").text.strip()}\n'
                           f'{z8[0].text.strip()}  {z8[1].text.strip()}  {z8[2].text.strip()}  '
                           f'{z8[3].text.strip()}  {z8[4].text.strip()}  {z8[5].text.strip()}  {z8[6].text.strip()}\n'
                           f'Тираж №{data[8].find("div", class_="draw").text.strip()} '
                           f'от {data[8].find("div", class_="draw_date").text.strip()}\n'
                           f'{z9[0].text.strip()}  {z9[1].text.strip()}  {z9[2].text.strip()}  '
                           f'{z9[3].text.strip()}  {z9[4].text.strip()}  {z9[5].text.strip()}  {z9[6].text.strip()}\n'
                           f'Тираж №{data[9].find("div", class_="draw").text.strip()} '
                           f'от {data[9].find("div", class_="draw_date").text.strip()}\n'
                           f'{z10[0].text.strip()}  {z10[1].text.strip()}  {z10[2].text.strip()}  '
                           f'{z10[3].text.strip()}  {z10[4].text.strip()}  {z10[5].text.strip()}  {z10[6].text.strip()}\n'
                           )


@dp.message_handler(lambda message: message.text == "Учить английский")
async def get_learn_english(message: types.Message):
    await message.reply("Раздел в разработке...")


@dp.message_handler()
async def get_weather(message: types.Message):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        # city = data["name"]
        city = message.text.lower().title()
        cur_weather = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp
        await message.reply(
            f"***{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}***\n"
            f"Погода в городе: {city}\nТемпература: {cur_weather}C°\n"
            f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст.\nВетер: {wind} м/с\n"
            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n"
            f"Продолжительность дня: {length_of_the_day}\n"
            f"***Хорошего дня!***"
            )
    except Exception as ex:
        await message.reply("Проверьте название города!")


if __name__ == '__main__':
    executor.start_polling(dp)
