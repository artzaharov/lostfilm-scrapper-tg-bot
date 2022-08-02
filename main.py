import requests
import smtplib
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types


def get_html(url):
    r = requests.get(url)
    return(r.text)


def send_email(title, txt):
    sender = ''  # email отправителя
    password = ''  # пароль для email отправителя
    receiver = ''  # email получателя

    message = f'From: <{sender}>\nTo: <{receiver}>\nSubject: Вышла новая серия - {title}\n{txt}'.encode('utf-8').strip()

    try:
        # mail = smtplib.SMTP_SSL('smtp.mail.ru', 468)  # SSL и нужно закомментировать убрать активацию TLS: mail.starttls()
        mail = smtplib.SMTP('smtp.mail.ru', 587)  # TLS
        mail.starttls()
        mail.login(sender, password)
        mail.sendmail(sender, receiver, message)
        mail.quit()
        print('email успешно отправлен')
    except Exception:
        print('Ошибка: невозможно отправить email!')


def get_data(html):
    soup = BeautifulSoup(html, 'lxml')

    serial_name = soup.find('h1').text.strip()
    trs = soup.find('table', class_='movie-parts-list').find('tr', class_='')
    last_episode_date = trs.find('td', class_='delta').text.split(':')[1].replace('Eng', '').strip()
    last_episode_title = trs.find('td', class_='beta').text.strip()
    current_date = datetime.now().strftime('%d.%m.%Y')

    if current_date == last_episode_date:
        return {'serial_name': serial_name, 'last_episode_title': last_episode_title}
    return None


URL = 'https://www.lostfilm.tv/series/The_Walking_Dead/seasons'  # URL страницы со всеми эпизодами вашего любимого сериала
TOKEN = ''  # Телеграм токен

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def send_answer(message: types.Message):
    await message.answer('Здесь не поддерживаются команды')


async def send_telegram_message():
    await bot.send_message('XXXXXXXXX', 'Вышла новая серия!' + ' ' + result['serial_name'] + ' ' + result['last_episode_title'])  # XXXXXXXXX - ваш ID чата в Телеграм

if __name__ == '__main__':
    # получаем данные с сайта
    result = get_data(get_html(URL))

    # если данные есть, отправляем email и/или сообщение в телеграм-бот
    if result:
        print('Вышла новая серия!', result['serial_name'], result['last_episode_title'])

        # отправляем email
        send_email(result['serial_name'], result['serial_name'] + ' ' + result['last_episode_title'])

        # отправляем сообщение в телеграм-бот
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(send_telegram_message())
            executor.start_polling(dp, skip_updates=True)
        except Exception:
            print('Ошибка: невозможно отправить сообщение телеграм-боту!')
