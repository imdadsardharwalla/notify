from .notify import TelegramNotify
import requests


class URLGet:

    def __init__(
        self, url: str, payload: dict, notify: TelegramNotify,
        failure_limit: int = 10):
        '''Create and initialise internal class variables.'''
        self._url = url
        self._payload = payload
        self._notify = notify
        self._failure_limit = failure_limit
        self._failure_count = 0

    def get(self):
        '''Attempt to access a URL. Provide helpful messages and notifications if this isn't possible.'''
        r = requests.get(self._url, params=self._payload)
        success = False

        # Check that we successfully connected to the URL
        if r.status_code == 200:  # success
            success = True
            self._notify.message(
                f'Accessed URL: {self._url} (payload: {self._payload})')

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
