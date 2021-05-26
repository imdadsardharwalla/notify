from datetime import datetime
import json
from pathlib import Path
import requests


_tokens = {}
_ids = {}
_default_id = None
_default_token = None


# Return timestamp in the following format: dd/mm/YY H:M:S
def get_timestamp():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# Load the list of bots/tokens and recipients/IDs from JSON files
def load_configurations(
    _bots_path='bots.json', _recipients_path='recipients.json'):

    global _tokens, _ids

    with Path(_bots_path).open('r') as f:
        _tokens = json.load(f)

    with Path(_recipients_path).open('r') as f:
        _ids = json.load(f)


# Set the default token and ID for the send() function (when only 1
# argument is passed)
def set_default_pathway(_bot_name, _recipient_name):
    global _default_id, _default_token

    _default_token = _tokens[_bot_name]
    _default_id = _ids[_recipient_name]


# Send a notification using the specified token and id. If these are not
# specified, the function attempts to use the default values. If these
# are not set, it fails to send the notification and displays an error
# message.
def send(_str, _token=None, _id=None):

    def print_info(_success, _str, _error_msg=None):
        print(f'{get_timestamp()}: ', end='')

        if _success:
            print('Notification sent: ', end='')
        else:
            error_msg = 'Unknown error' if _error_msg is None else _error_msg
            print(f'Notification FAILED [{error_msg}]: ', end='')

        print(f'"{_str}"')

    # If None, replace the token and id with the default ones
    if _token is None:
        _token = _default_token

    if _id is None:
        _id = _default_id

    # If still None, print an error
    if _token is None:
        print_info(False, _str, 'No bot token was provided')
        return

    if _id is None:
        print_info(False, _str, 'No recipient ID was provided')
        return

    url = f"https://api.telegram.org/bot{_token}"
    params = {'chat_id': _id, 'text': _str}

    r = requests.get(url + "/sendMessage", params=params)
    print_info(r.status_code == 200, _str, f'Status code was {r.status_code}')


# Print a line of information to stdout
def info(_str):
    print(f'{get_timestamp()}: Info: {_str}')
