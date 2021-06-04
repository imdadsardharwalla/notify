#!/usr/bin/python3

from datetime import datetime
import json
from pathlib import Path
import requests

from lib.urlget import URLGet


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / 'config'


def load_token():
    with (CONFIG_DIR / 'token').open('r') as f:
        token = f.readline().strip()

        # Check the token does not contain invalid characters
        allowed_chars = (
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            '0123456789-._~:/?#[]@!$&\'()*+,;=')

        for char in token:
            if char not in allowed_chars:
                raise ValueError(f'"{token}" is not a valid token.')

        # Check the token is not too short
        if len(token) < 12:
            raise ValueError(f'"{token}" is not a valid token.')

    return token


def load_recipients():
    with (CONFIG_DIR / 'recipients.json').open('r') as f:
        recipients = json.load(f)

    return recipients


def load_notifiers():
    with (CONFIG_DIR / 'notifiers.json').open('r') as f:
        notifiers = json.load(f)

    return notifiers


token = load_token()
recipients = load_recipients()
notifiers = load_notifiers()
base_url = f'https://api.telegram.org/bot{token}'


def url_to_json(url: URLGet):
    success, r = url.get()

    if not success:
        return None

    json_text = r.content.decode('utf-8', 'ignore')
    # TODO exception handling here
    json_struct = json.loads(json_text)

    return json_struct


def build_url(stem: str, options: dict) -> str:
    options_str = ''
    if len(options) > 0:
        for option, value in options.items():
            options_str += f'&{option}={value}'

        options_str = '?' + options_str[1:]
    return stem + options_str


def get_updates(offset=None, timeout: int = 100):
    options = {}
    if timeout:
        options['timeout'] = timeout

    if offset:
        options['offset'] = offset

    update_url = URLGet(build_url(f'{base_url}/getUpdates', options))
    return url_to_json(update_url)


def get_max_update_id(updates):
    max_update_id = 0
    for update in updates['result']:
        max_update_id = max(max_update_id, int(update['update_id']))
    return max_update_id


def get_recipient_id(update):
    return str(update['message']['from']['id'])


def is_bot(update):
    return update['message']['from']['is_bot']


def get_message_text(update):
    return update['message']['text'].strip()


def get_timestamp():
    '''Return timestamp in the following format: dd/mm/YY H:M:S'''
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def print_message(text: str):
    '''Prints text to stdout.'''
    print(f'{get_timestamp()}: {text}')


def notification_message(success: bool, text: str,
                         error_msg: str = 'Error not specified') -> bool:
    '''Printa a message about the success of the notification. Returns the success variable.'''
    if success:
        message = 'Notification sent: '
    else:
        message = f'Notification FAILED [{error_msg}]: '
    message += f'"{text}"'

    print_message(message)
    return success


def send_notification(id, text: str) -> bool:
    params = {'chat_id': id, 'text': text}
    r = requests.get(f'{base_url}/sendMessage', params=params)

    # TODO also send recipient name
    return notification_message(
        r.status_code == 200,
        text,
        f'Status code was {r.status_code}')


# Ignore all messages from before the script was started
updates = get_updates(None, None)
offset = get_max_update_id(updates) + 1

while True:
    updates = get_updates(offset)
    offset = get_max_update_id(updates) + 1

    print(updates)

    for update in updates['result']:
        if is_bot(update):
            print(f'Bots are not authorised.')
            continue

        recipient_id = get_recipient_id(update)

        if recipient_id not in recipients.keys():
            print(f'{recipient_id} is not an authorised recipient.')
            continue

        message_text = get_message_text(update)

        print_message(f'Message received from {recipients[recipient_id]}: {message_text}')

        send_notification(recipient_id, message_text)
