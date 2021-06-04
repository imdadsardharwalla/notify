import json
from pathlib import Path


_CONFIG_DIR = Path(__file__).resolve().parent


def load_token():
    with (_CONFIG_DIR / 'token').open('r') as f:
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


def load_users():
    with (_CONFIG_DIR / 'users.json').open('r') as f:
        users = json.load(f)

    return users


def load_notifiers():
    with (_CONFIG_DIR / 'notifiers.json').open('r') as f:
        notifiers = json.load(f)

    return notifiers
