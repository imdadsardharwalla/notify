from datetime import datetime
import json
from pathlib import Path
import requests


def get_timestamp():
    '''Return timestamp in the following format: dd/mm/YY H:M:S'''
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class TelegramNotify:

    def __init__(self):
        '''Create and initialise internal class variables.'''
        self._tokens = {}
        self._IDs = {}
        self._ID = None
        self._token = None

    def load_pathways(
            self, bots_path='bots.json', recipients_path='recipients.json'):
        '''Load the list of bots/tokens and recipients/IDs from JSON files.'''

        with Path(bots_path).open('r') as f:
            self._tokens = json.load(f)

        with Path(recipients_path).open('r') as f:
            self._IDs = json.load(f)

    def set_pathway(self, bot_name, recipient_name):
        '''Set the token and ID to be used by the send() function.'''
        self._token = self._tokens[bot_name]
        self._ID = self._IDs[recipient_name]

    def send(self, text):
        '''Send a notification using the set pathway.'''

        def print_line(_success, text, error_msg='Error not specified'):
            print(f'{get_timestamp()}: ', end='')

            if _success:
                print('Notification sent: ', end='')
            else:
                print(f'Notification FAILED [{error_msg}]: ', end='')

            print(f'"{text}"')

        # If no token has been set, print an error
        if self._token is None:
            print_line(
                False, text,
                'No bot token was provided. Did you call set_pathway()?')
            return

        # If no ID has been set, print an error
        if self._ID is None:
            print_line(
                False, text,
                'No recipient ID was provided. Did you call set_pathway()?')
            return

        url = f"https://api.telegram.org/bot{self._token}"
        params = {'chat_id': self._ID, 'text': text}

        r = requests.get(url + "/sendMessage", params=params)
        print_line(
            r.status_code == 200, text, f'Status code was {r.status_code}')

    def info(self, text):
        '''Print a line of information to stdout.'''
        print(f'{get_timestamp()}: Info: {text}')
