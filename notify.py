from datetime import datetime
import json
from pathlib import Path
import requests


def get_timestamp():
    '''Return timestamp in the following format: dd/mm/YY H:M:S'''
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class Notify:

    def __init__(self, name: str):
        self._name = name

    def get_notification_text(self, text: str) -> str:
        return f'{self._name}: {text}'

    def message(self, text: str):
        '''Prints text to stdout.'''
        print(f'{get_timestamp()}: {text}')

    def notification_message(self, success: bool, text: str, id: str,
                             error_msg: str = 'Error not specified') -> bool:
        '''Printa a message about the success of the notification. Returns the success variable.'''
        if success:
            message = f'Notification sent -> {id}: '
        else:
            message = f'Notification FAILED -> {id} [{error_msg}]: '
        message += f'"{text}"'

        self.message(message)
        return success

    def send(self, text: str) -> bool:
        '''Placeholder for a subclass method.'''
        raise NotImplementedError('Override this with a subclass method.')

    def test_pathway(self):
        '''Placeholder for a subclass method.'''
        raise NotImplementedError('Override this with a subclass method.')


class TelegramNotify(Notify):

    def __init__(self, name: str):
        '''Create and initialise internal class variables.'''
        super().__init__(name)
        self._tokens = {}
        self._IDs = {}
        self._ID = None
        self._token = None

    def load_pathways(
            self, bots_path='telegram-bots.json',
            recipients_path='telegram-recipients.json'):
        '''Load the list of bots/tokens and recipients/IDs from JSON files.'''

        with Path(bots_path).open('r') as f:
            self._tokens = json.load(f)

        with Path(recipients_path).open('r') as f:
            self._IDs = json.load(f)

    def set_pathway(self, bot_name: str, recipient_name: str):
        '''Set the token and ID to be used by the send() function.'''
        self._token = self._tokens[bot_name]
        self._ID = self._IDs[recipient_name]

    def send(self, text: str) -> bool:
        '''Send a notification using the set pathway. Returns True/False on success/failure.'''
        notification_text = self.get_notification_text(text)

        # If no token or ID has been set, print an error
        if not self._token or not self._ID:
            return self.notification_message(
                False,
                notification_text,
                None,
                'Either bot token or recipient ID was empty. Did you call set_pathway()?')

        url = f"https://api.telegram.org/bot{self._token}"
        params = {'chat_id': self._ID, 'text': notification_text}

        r = requests.get(url + "/sendMessage", params=params)
        return self.notification_message(
            r.status_code == 200,
            notification_text,
            self._ID,
            f'Status code was {r.status_code}')

    def test_pathway(self):
        '''Send a test notification.'''
        self.message('Testing pathway...')
        if not self.send('Pathway test notification.'):
            raise RuntimeError('Pathway test failed.')
