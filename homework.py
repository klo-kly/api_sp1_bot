import os
import time
import requests
import telegram
from dotenv import load_dotenv
import logging

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s,'
           ' (%(filename)s).%(funcName)s(%(lineno)d), %(message)s'
)
logger = logging.getLogger('__name__')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    logging.debug('Получение статуса домашки')
    current_timestamp = current_timestamp or int(time.time())
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logger.info('Сообщение отправлено')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    flag = True
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if homeworks['homeworks']:
                flag = True
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
            else:
                if flag:
                    send_message('Сданных работ на проверку не найдено')
                    flag = False
                time.sleep(5)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой запроса: {e}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
