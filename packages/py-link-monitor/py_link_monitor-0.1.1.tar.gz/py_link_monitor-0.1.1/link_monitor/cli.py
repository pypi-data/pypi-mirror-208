from time import time, sleep
from argparse import ArgumentParser

from link_monitor.monitor import LinkMonitor


class MonitorCLI:

    def __init__(self, options):
        self._options = options
        self._monitor = LinkMonitor(self._options.target)
        self._interval = self._options.interval

        self._started_at = None

    def pre_sleep(self):
        self._started_at = time()

    def sleep(self):
        now = time()
        sleep_for = (now - self._started_at - self._interval) * -1
        if sleep_for > 0:
            sleep(sleep_for)

    def run_forever(self):
        while True:
            self.pre_sleep()
            try:
                self._monitor.check()
            finally:
                self.sleep()


def run_cli():
    parser = ArgumentParser(description='Monitor bandwidth of interface')
    parser.add_argument('--target', '-t', required=True, type=str)
    parser.add_argument('--interval', '-i', required=False, type=int, default=1)
    MonitorCLI(parser.parse_args()).run_forever()


if __name__ == '__main__':
    class TestOptions:
        target = '8.8.8.8'
        interval = 1

    MonitorCLI(TestOptions).run_forever()
