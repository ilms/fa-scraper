import time


class Cooldown:
    """
    Cooldown is a decorator ensures a specific amount of time is passed between function calls.

    Lets say a Cooldown(5) is used as a decorator.
    Calling the function for the first time will run immediately.
    Calling the function a second time will wait 5 seconds before running.
    These 5 seconds include any combination of time spent between the functions
    and a forced sleep to ensure a total wait of 5 seconds.
    This means if the second function call is 10 seconds after the first,
    then the function will run immediately.
    """
    def __init__(self, duration: int = 1):
        """
        Defines a new cooldown.

        :param duration: The number of seconds to wait between function calls.
        """
        self._duration = duration
        self._start = time.time() - duration

    def _wait(self):
        while time.time() - self._start < self._duration:
            time.sleep(self._duration + self._start - time.time())

    def _reset(self):
        self._start = time.time()

    def __call__(self, f):
        def wrap(*args, **kwargs):
            self._wait()
            f(*args, **kwargs)
            self._reset()
        return wrap
