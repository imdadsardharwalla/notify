#!/usr/bin/python3

from datetime import datetime
import json
from pathlib import Path
import requests

from config import config
from lib.urlget import URLGet


# TODO all of this needs error handling


token = config.load_token()
users = config.load_users()
notifiers = config.load_notifiers()
base_url = f'https://api.telegram.org/bot{token}'


def url_to_json(url: URLGet):
    success, r = url.get()

    if not success:
        return None

    json_text = r.content.decode('utf-8', 'ignore')
    # TODO exception handling here
    json_struct = json.loads(json_text)

    return json_struct


# TODO can this be replaced using params as in send_notification()?
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


def get_id(update):
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


# TODO want this to retry a few times
def send_notification(id, text: str) -> bool:
    params = {'chat_id': id, 'text': text, 'parse_mode': 'html'}
    r = requests.get(f'{base_url}/sendMessage', params=params)

    # TODO also send user name
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

    for update in updates['result']:
        # Ignore message if it has come from a bot
        if is_bot(update):
            print(f'Bots are not authorised.')
            continue

        # Get the ID of the sender
        id = get_id(update)

        if id not in users.keys():
            send_notification(
                id, 'Hello! You\'re not currently authorised to communicate '
                'with this notify server. Please speak to the admin of the '
                f'server and ask them to add your ID ({id}) to the list of '
                'authorised users.')

            print(f'Communcation is not authorised for {id}.')
            continue

        message_text = get_message_text(update)

        print_message(
            f'Message received from {users[id]}: {message_text}')

        response_text = 'some usage text here'

        if message_text == '/start':
            send_notification(id, f'Hello, {users[id]}!')
        if message_text == '/list_all':
            # List all notifiers
            if len(notifiers.keys()) == 0:
                response_text = 'No notifiers are available.'
            else:
                response_text = 'The available notifiers are:\n\n'

                for name, data in notifiers.items():
                    response_text += (f' - <b>{name}</b>: '
                                      f'<i>{data["description"]}</i>\n')

            send_notification(id, response_text)
        elif message_text == '/ping':
            send_notification(id, 'Yes, I\'m still here!')
