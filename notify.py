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

    def message(self, text: str):
        '''Prints text to stdout.'''
        print(f'{get_timestamp()}: {text}')

    def load_pathways(
            self, bots_path='bots.json', recipients_path='recipients.json'):
        '''Load the list of bots/tokens and recipients/IDs from JSON files.'''

        with Path(bots_path).open('r') as f:
            self._tokens = json.load(f)

        with Path(recipients_path).open('r') as f:
            self._IDs = json.load(f)

    def notification_message(self, success: bool, text: str,
                                error_msg: str = 'Error not specified') -> bool:
        '''Printa a message about the success of the notification. Returns the success variable.'''
        if success: message = 'Notification sent: '
        else: message = f'Notification FAILED [{error_msg}]: '
        message += f'"{text}"'

        self.message(message)
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
            return self.notification_message(
                False,
                notification_text,
                'No bot token was provided. Did you call set_pathway()?')

        # If no ID has been set, print an error
        if self._ID is None:
            return self.notification_message(
                False,
                notification_text,
                'No recipient ID was provided. Did you call set_pathway()?')

        url = f"https://api.telegram.org/bot{self._token}"
        params = {'chat_id': self._ID, 'text': notification_text}

        r = requests.get(url + "/sendMessage", params=params)
        return self.notification_message(
            r.status_code == 200,
            notification_text,
            f'Status code was {r.status_code}')

    def test_pathway(self):
        '''Send a test notification.'''
        self.message('Testing pathway...')
        if not self.send('Pathway test notification.'):
            raise RuntimeError('Pathway test failed.')


class URLGet:

    def __init__(self, url:str, notify: TelegramNotify, failure_limit:int=10):
        '''Create and initialise internal class variables.'''
        self._url = url
        self._notify = notify
        self._failure_limit = failure_limit
        self._failure_count = 0

    def get(self):
        '''Attempt to access a URL. Provide helpful messages and notifications if this isn't possible.'''
        r = requests.get(self._url)
        success = False

        # Check that we successfully connected to the URL
        if r.status_code == 200:  # success
            success = True
            self._notify.message(f'Accessed URL: {self._url}')

            if self._failure_count > 0:
                self._notify.send(f'Reconnected to the URL after {self._failure_count} failure(s): {self._url}')
                self._failure_count = 0
        else:  # failure
            self._notify.message(f'Failed to access URL: {self._url}')
            self._failure_count += 1

            # Send a warning notification if we haven't been able to
            # connect to the URL multiple times
            if self._failure_count >= self._failure_limit:
                self._notify.send(f'Unable to reach URL (tried {self._failure_count} time(s)): {self._url}')

        return [success, r]