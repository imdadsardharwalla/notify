#!/usr/bin/python3

import json
from pathlib import Path

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


token = load_token()
recipients = load_recipients()
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


# Ignore all messages from before the script was started
updates = get_updates(None, None)
offset = get_max_update_id(updates) + 1


updates = get_updates(offset)
offset = get_max_update_id(updates) + 1
print(updates)
