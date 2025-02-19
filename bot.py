import argparse
import textwrap
import logging
import requests
import telegram
import time
import os

from dotenv import load_dotenv
from time import sleep


URL = 'https://dvmn.org/api/long_polling/'


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    bot_token = os.environ['TG_BOT_TOKEN']
    headers = {'Authorization': f'Token {devman_token}'}
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=bot_token)
    bot.logger.addHandler(TelegramLogsHandler(bot, chat_id))
    bot.logger.warning('Бот запущен')
    timestamp = ''
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    while True:
        try:
            response = requests.get(URL,
                                    headers=headers,
                                    params={"timestamp": timestamp},
                                    timeout=90,)
            response.raise_for_status()
            check_results = response.json()
            if check_results["status"] == "timeout":
                timestamp = check_results["timestamp_to_request"]
            else:
                timestamp = check_results["new_attempts"][0]["timestamp"]
                is_negative = check_results["new_attempts"][0]["is_negative"]
                lesson_title = (
                    check_results["new_attempts"][0]["lesson_title"]
                )
                lesson_url = check_results["new_attempts"][0]["lesson_url"]

            if is_negative:
                bot.send_message(
                    text=textwrap.dedent(f'''
                    У вас проверили работу «{lesson_title}»\n
                    К сожалению в работе нашлись ошибки.
                    Ссылка на урок:{lesson_url}
                    '''),
                    chat_id=chat_id,
                    )
            else:
                bot.send_message(
                    text=textwrap.dedent(f'''
                    У вас проверили работу «{lesson_title}»\n
                    Преподаватель одобрил работу, можно приступать
                    к следующему уроку! Ссылка на урок:{lesson_url}
                    '''),
                    chat_id=chat_id,
                    )
        except requests.exceptions.ConnectionError:
            sleep(10)
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as err:
            error = f'Бот упал с ошибкой {str(err)}'
            bot.logger.warning(error)


if __name__ == "__main__":
    main()