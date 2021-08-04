import os
import time
import requests
import logging

import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YA_HOMEWORK = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s,'
           ' (%(filename)s).%(funcName)s(%(lineno)d), %(message)s'
)
logger = logging.getLogger('__name__')

VERDICT = {
    'rejected': 'К сожалению, в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'reviewing': 'Работа в процессе проверки',
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        return f'{homework_name} отсутствует'
    return (f'У вас проверили работу "{homework_name}"!'
            f'\n\n{VERDICT[homework_status]}')


def get_homeworks(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
    logging.debug('Получение статуса домашки')
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL_YA_HOMEWORK,
                                         headers=HEADERS,
                                         params=payload
                                         )
    except requests.exceptions.RequestException:
        raise
    return homework_statuses.json()


def send_message(message):
    logger.info('Сообщение отправлено')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if homeworks['homeworks']:
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
                current_timestamp = homeworks['current_date']
            else:
                if message == 'Сданных работ на проверку не найдено':
                    continue
                message = 'Сданных работ на проверку не найдено'
                send_message(message)
                time.sleep(5)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой запроса: {e}')
            print(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
