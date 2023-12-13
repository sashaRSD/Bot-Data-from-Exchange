from datetime import datetime
import requests, string, fake_useragent
from dir_base import sqlite_db
from dir_bot import create_bot
ua = fake_useragent.UserAgent()


def get_name_moex(moex_value):
    moex_value = moex_value.translate(str.maketrans('', '', string.punctuation))

    try:
        url_data = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
        headers = {"User-Agent": ua.random}
        req = requests.get(url_data, headers=headers).json()
        data = req["marketdata"]["data"]
        name = req["securities"]["data"]
    except requests.exceptions.ConnectionError:
        print('[!] Data loading error!')
        return '[!] Data loading error!'

    for iname in name:
        if iname[0].lower() == moex_value.lower() or moex_value.lower() in iname[2].lower():
            for i in data:
                if i[0].lower() == iname[0].lower():
                    if i[4] is not None:
                        return f"{iname[2]}\n /{i[0]} price {i[4]} ({i[25]}%)\n"
                    elif i[12] is not None:
                        return f"{iname[2]}\n /{i[0]} price {i[12]} ({i[25]}%)*\n"
                    else:
                        return f" {iname[0].upper()} price ERROR\n"
    return 'O_o Не могу найти такую акцию \n' \
            'Пример ввода: GAZP или Газпром\n\n' \
            'Получить значения вашего списка: /set\n'\
            'Настроить вывод списка: /setup\n'


def get_cripto(cryptocurrency_value):
    text = f"\nCryptocurrency:\n"

    try:
        req = requests.get(f"https://api.cryptorank.io/v1/currencies?api_key={create_bot.config['TOKEN']['token_api_cripto']}").json()["data"]
    except requests.exceptions.ConnectionError:
        print('[!] Data loading error!')
        return"\nCryptocurrency:\n [!] Data loading error!"

    for i in req:
        for ticket in cryptocurrency_value:
            if str(i["symbol"]).lower() == ticket.lower():
                if i['values']['USD']['price'] > 1:
                    text += f" {i['symbol'] } price {round(i['values']['USD']['price'], 1)}\n"
                else:
                    text += f" {i['symbol']} price {round(i['values']['USD']['price'], 5)}\n"
    return text


def get_moex(moex_value):
    text = '\nStock MOEX:\n'

    try:
        url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
        headers = {"User-Agent": ua.random}
        req = requests.get(url, headers=headers).json()["marketdata"]["data"]
    except requests.exceptions.ConnectionError:
        print('[!] Data loading error!')
        return '\nStock MOEX:\n [!] Data loading error!'

    for i in req:
        for ticket in moex_value:
            if i[0].lower() == ticket.lower():
                if i[4] is not None:
                    text += f" /{i[0]} price {i[4]} ({i[25]}%)\n"
                elif i[12] is not None:
                    text += f" /{i[0]} price {i[12]} ({i[25]}%)*\n"
                else:
                    text += f" {ticket.upper()} price ERROR\n"

    return text


def get_currency(currency_value):
    text = f"\nCurrency:\n"

    try:
        url = "https://iss.moex.com/iss/statistics/engines/currency/markets/selt/rates/securities.json"
        headers = {"User-Agent": ua.random}
        req = requests.get(url, headers=headers).json()['wap_rates']['data']
    except requests.exceptions.ConnectionError:
        print('[!] Data loading error!')
        return "\nCurrency:\n [!] Data loading error!"

    for i in req:
        for ticket in currency_value:
            if str(i[3]).lower()[:3] == ticket.lower():
                text += f" {ticket.upper()} price {round(i[4],2)}\n"
    return text


async def set_data(id):
    text = f"\nTime:\n{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
    moex_value = ['GAZP', 'SBER', 'LKOH', 'GMKN', 'NVTK', 'YNDX', 'ROSN', 'MGNT', 'TCSG', 'PLZL',
                  'TATN', 'PHOR', 'SNGS', 'MTSS', 'CHMF', 'FIVE', 'ALRS', 'SNGSP', 'MOEX', 'NLMK',
                  'POLY', 'SBERP', 'IRAO', 'OZON', 'RUAL', 'PIKK', 'VTBR', 'MAGN', 'VKCO', 'RTKM',
                  'CBOM', 'TRNFP', 'HYDR', 'TATNP', 'FIXP', 'AFKS', 'ENPG', 'GLTR', 'AFLT', 'SGZH']
    currency_value = ['USD', 'EUR', 'CNY']
    cryptocurrency_value = ['btc', 'eth', 'doge']

    bd_read = await sqlite_db.sql_read(id)
    if bd_read:
        if bd_read[0][1] == 'да':
            text += get_moex(moex_value)
        if bd_read[0][2] == 'да':
            text += get_currency(currency_value)
        if bd_read[0][3] == 'да':
            text += get_cripto(cryptocurrency_value)
        if 'да' not in bd_read[0]:
            text += '\nВы всё отключили...\nДля включения перейдите в настройки ;)'
    else:
        text += get_moex(moex_value) + get_currency(currency_value) + get_cripto(cryptocurrency_value)
    return text
