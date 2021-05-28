import time


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
                f'Sleeper: Waiting for {self._wait_str} ({self._seconds} '
                'seconds)...',
                end='',
                flush=True)

        time.sleep(self._seconds)

        if self._print_status:
            print('done.')

        return True
