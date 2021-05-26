from datetime import datetime
import json
from pathlib import Path
import requests


# Return timestamp in the following format: dd/mm/YY H:M:S
def get_timestamp():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class TelegramNotify:


    def __init__(self):
        self._tokens = {}
        self._IDs = {}
        self._ID = None
        self._token = None


    # Load the list of bots/tokens and recipients/IDs from JSON files
    def load_pathways(
            self, bots_path='bots.json', recipients_path='recipients.json'):

        with Path(bots_path).open('r') as f:
            self._tokens = json.load(f)

        with Path(recipients_path).open('r') as f:
            self._IDs = json.load(f)


    # Set the token and ID to be used by the send() function
    def set_pathway(self, bot_name, recipient_name):
        self._token = self._tokens[bot_name]
        self._ID = self._IDs[recipient_name]


    # Send a notification using the set pathway
    def send(self, text):

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


    # Print a line of information to stdout
    def info(self, text):
        print(f'{get_timestamp()}: Info: {text}')
