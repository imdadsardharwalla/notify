from datetime import datetime
import json
from pathlib import Path
import requests


def get_timestamp():
    '''Return timestamp in the following format: dd/mm/YY H:M:S'''
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class TelegramNotify:

    def __init__(self, name: str):
        '''Create and initialise internal class variables.'''
        self._tokens = {}
        self._IDs = {}
        self._ID = None
        self._token = None
        self._name = name

    def print_info(self, text: str):
        '''Print a line of information to stdout.'''
        print(f'{get_timestamp()}: Info: {text}')

    def load_pathways(
            self, bots_path='bots.json', recipients_path='recipients.json'):
        '''Load the list of bots/tokens and recipients/IDs from JSON files.'''

        with Path(bots_path).open('r') as f:
            self._tokens = json.load(f)

        with Path(recipients_path).open('r') as f:
            self._IDs = json.load(f)

    def print_notification_info(self, success: bool, text: str,
                                error_msg: str = 'Error not specified') -> bool:
        '''Print an info line to stdout about the success of the notification. Returns success variable.'''
        print(f'{get_timestamp()}: ', end='')
        if success:
            print('Notification sent: ', end='')
        else:
            print(f'Notification FAILED [{error_msg}]: ', end='')
        print(f'"{text}"')

        return success

    def set_pathway(self, bot_name: str, recipient_name: str):
        '''Set the token and ID to be used by the send() function.'''
        self._token = self._tokens[bot_name]
        self._ID = self._IDs[recipient_name]

    def send(self, text: str) -> bool:
        '''Send a notification using the set pathway. Returns True/False on success/failure.'''
        notification_text = f'{self._name}: {text}'

        # If no token has been set, print an error
        if self._token is None:
            return self.print_notification_info(
                False,
                notification_text,
                'No bot token was provided. Did you call set_pathway()?')

        # If no ID has been set, print an error
        if self._ID is None:
            return self.print_notification_info(
                False,
                notification_text,
                'No recipient ID was provided. Did you call set_pathway()?')

        url = f"https://api.telegram.org/bot{self._token}"
        params = {'chat_id': self._ID, 'text': notification_text}

        r = requests.get(url + "/sendMessage", params=params)
        return self.print_notification_info(
            r.status_code == 200,
            notification_text,
            f'Status code was {r.status_code}')

    def test_pathway(self):
        '''Send a test notification.'''
        self.print_info('Testing pathway...')
        if not self.send('Pathway test notification.'):
            raise RuntimeError('Pathway test failed.')
