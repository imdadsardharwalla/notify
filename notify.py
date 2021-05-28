from datetime import datetime
import json
from pathlib import Path
import requests
import time


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

    def notification_message(self, success: bool, text: str,
                             error_msg: str = 'Error not specified') -> bool:
        '''Printa a message about the success of the notification. Returns the success variable.'''
        if success:
            message = 'Notification sent: '
        else:
            message = f'Notification FAILED [{error_msg}]: '
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

    def __init__(
            self, url: str, notify: TelegramNotify, failure_limit: int = 10):
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
                self._notify.send(
                    f'Reconnected to the URL after {self._failure_count} '
                    f'failure(s): {self._url}')
                self._failure_count = 0
        else:  # failure
            self._notify.message(f'Failed to access URL: {self._url}')
            self._failure_count += 1

            # Send a warning notification if we haven't been able to
            # connect to the URL multiple times
            if self._failure_count >= self._failure_limit:
                self._notify.send(
                    f'Unable to reach URL (tried {self._failure_count} '
                    f'time(s)): {self._url}')

        return [success, r]


class Sleeper:

    def __init__(
            self, num_units: float, unit: str = 'seconds',
            skip_initial: bool = True, print_status: bool = False):

        num_units_f = float(num_units)

        unit_lc = unit.lower()
        if unit_lc == 's':
            unit_lc = 'seconds'
        elif unit_lc == 'm':
            unit_lc = 'minutes'
        elif unit_lc == 'h':
            unit_lc = 'hours'
        elif unit_lc == 'd':
            unit_lc = 'days'

        if num_units_f < 0:
            raise ValueError(f'"{num_units}" should be a non-negative value')

        if unit_lc == 'seconds':
            self._seconds = num_units_f
        elif unit_lc == 'minutes':
            self._seconds = num_units_f * 60
        elif unit_lc == 'hours':
            self._seconds = num_units_f * 60 * 60
        elif unit_lc == 'days':
            self._seconds = num_units_f * 60 * 60 * 24
        else:
            raise ValueError(
                f'"{unit}" should be one of the following: "seconds", '
                '"s", "minutes", "m", "hours", "h", "days", "d"')

        self._skip_initial = skip_initial
        self._initial = True

        self._print_status = print_status
        self._wait_str = f'{num_units_f} {unit_lc}'

    def wait(self):
        if self._initial and self._skip_initial:
            self._initial = False
            if self._print_status:
                print('Sleeper: Skipping initial wait...')
            return True

        if self._print_status:
            print(
                f'Sleeper: Waiting for {self._wait_str}...',
                end='',
                flush=True)

        time.sleep(self._seconds)

        if self._print_status:
            print('done.')

        return True
