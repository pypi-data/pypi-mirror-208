from time import time
from datetime import datetime

from link_monitor.ping import is_alive
from link_monitor.logger import info


class LinkMonitor:
    STATUS_ALIVE = 'ALIVE'
    STATUS_FAIL = 'FAIL'

    def __init__(self, target: str):
        self._target = target

        self._status = self.STATUS_FAIL

        self._created_at = time()
        self._changed_at = self._created_at
        self._checked_at = None

    @property
    def is_alive(self) -> bool:
        return self._status == self.STATUS_ALIVE

    @property
    def changed_at_str(self):
        return datetime.fromtimestamp(self._changed_at).isoformat()

    def set_status(self, status):
        self._status = status
        self._changed_at = time()
        info(f'Status changed to {self._status} for monitor of {self._target} at {self.changed_at_str}')

    def set_alive(self):
        self.set_status(self.STATUS_ALIVE)

    def set_fail(self):
        self.set_status(self.STATUS_FAIL)

    def check(self):
        is_alive_result = is_alive(
            self._target
        )

        if not is_alive_result and self.is_alive:
            self.set_fail()

        elif is_alive_result and not self.is_alive:
            self.set_alive()
