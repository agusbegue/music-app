import requests

from musically.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_CHAT_ID


def report(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_BOT_CHAT_ID}&&text={message}'
    requests.get(url)
