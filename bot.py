import textwrap
import logging
import requests
import telegram
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
        try:
            self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)
        except Exception:
            pass


def main():
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    bot_token = os.environ['TG_BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']

    bot = telegram.Bot(token=bot_token)

    logger = logging.getLogger('DevmanBot')
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('/opt/devman/DevmanCheckBot/bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    tg_handler = TelegramLogsHandler(bot, chat_id)
    tg_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(tg_handler)

    logger.info('Бот запущен успешно.')

    headers = {'Authorization': f'Token {devman_token}'}
    timestamp = ''

    while True:
        try:
            response = requests.get(URL, headers=headers, params={"timestamp": timestamp}, timeout=90)
            response.raise_for_status()
            check_results = response.json()

            if check_results["status"] == "timeout":
                timestamp = check_results["timestamp_to_request"]
                continue

            attempt = check_results["new_attempts"][0]
            timestamp = attempt["timestamp"]
            lesson_title = attempt["lesson_title"]
            lesson_url = attempt["lesson_url"]
            is_negative = attempt["is_negative"]

            if is_negative:
                text = textwrap.dedent(f"""
                    У вас проверили работу «{lesson_title}» 😞
                    К сожалению, в работе нашлись ошибки.
                    Ссылка на урок: {lesson_url}
                """)
            else:
                text = textwrap.dedent(f"""
                    У вас проверили работу «{lesson_title}» 🎉
                    Преподаватель одобрил работу! Можно приступать к следующему уроку.
                    Ссылка на урок: {lesson_url}
                """)

            bot.send_message(chat_id=chat_id, text=text.strip())

        except requests.exceptions.ConnectionError:
            logger.warning('Проблема с соединением. Переподключение через 10 секунд...')
            sleep(10)
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as err:
            logger.exception(f'Бот упал с ошибкой: {err}')


if __name__ == "__main__":
    main()
