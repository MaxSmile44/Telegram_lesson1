import os

import requests
import telegram

from dotenv import load_dotenv
from time import sleep


def send_tg_message(tg_token, chat_id, text):
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=chat_id, text=text)


def looking_for_completed_works(dev_token, tg_token, chat_id):
    headers = {'Authorization': f'Token {dev_token}'}
    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers)
            response.raise_for_status()
            work_data = response.json()
            if work_data['status'] == 'found':
                if work_data['new_attempts'][0]['is_negative']:
                    send_tg_message(
                        tg_token, chat_id,
                        f"У вас проверили работу \"{work_data['new_attempts'][0]['lesson_title']}\"\n\n"
                        f"К сожалению, в работе нашлись ошибки.\n"
                        f"{work_data['new_attempts'][0]['lesson_url']}"
                    )
                else:
                    send_tg_message(
                        tg_token, chat_id,
                        f"У вас проверили работу \"{work_data['new_attempts'][0]['lesson_title']}\"\n\n"
                        f"Преподавателю всё понравилось, можно приступать к следующему уроку!\n"
                        f"{work_data['new_attempts'][0]['lesson_url']}"
                    )
            print(work_data)
        except requests.ReadTimeout:
            print('Таймаут вышел')
        except requests.exceptions.ConnectionError:
            print('Отсутствует подключение к интернету')
            sleep(10)


def main():
    try:
        load_dotenv()
        dev_token = os.environ['DEVMAN_TOKEN']
        tg_token = os.environ['TG_TOKEN']
        chat_id = os.environ['CHAT_ID']
    except KeyError as error:
        print(f'KeyError: {error}')
        raise SystemExit
    looking_for_completed_works(dev_token, tg_token, chat_id)


if __name__ == '__main__':
    main()
