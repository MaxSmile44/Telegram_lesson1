import logging
import os

import requests
import telegram

from dotenv import load_dotenv
from time import sleep


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=tg_token)
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


logger = logging.getLogger()


def send_tg_message(tg_token, chat_id, text):
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=chat_id, text=text)


def looking_for_completed_works(dev_token, tg_token, chat_id):
    headers = {'Authorization': f'Token {dev_token}'}
    while True:
        try:
            logger.info('Бот запущен')
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers)
            response.raise_for_status()
            task_status = response.json()
            if task_status['status'] == 'found':
                if task_status['new_attempts'][0]['is_negative']:
                    send_tg_message(
                        tg_token, chat_id,
                        f"У вас проверили работу \"{task_status['new_attempts'][0]['lesson_title']}\"\n\n"
                        f"К сожалению, в работе нашлись ошибки.\n"
                        f"{task_status['new_attempts'][0]['lesson_url']}"
                    )
                else:
                    send_tg_message(
                        tg_token, chat_id,
                        f"У вас проверили работу \"{task_status['new_attempts'][0]['lesson_title']}\"\n\n"
                        f"Преподавателю всё понравилось, можно приступать к следующему уроку!\n"
                        f"{task_status['new_attempts'][0]['lesson_url']}"
                    )
        except requests.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logger.warning('Отсутствует подключение к интернету')
            sleep(10)
        except Exception as err:
            logger.exception(err)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    try:
        dev_token = os.environ['DEVMAN_TOKEN']
        tg_token = os.environ['TG_TOKEN']
        chat_id = os.environ['CHAT_ID']
    except KeyError as error:
        print(f'KeyError: {error}')
        raise SystemExit

    tg_handler = TelegramLogsHandler(tg_token, chat_id)
    tg_handler.setLevel(logging.INFO)
    logger.addHandler(tg_handler)

    looking_for_completed_works(dev_token, tg_token, chat_id)


if __name__ == '__main__':
    main()
