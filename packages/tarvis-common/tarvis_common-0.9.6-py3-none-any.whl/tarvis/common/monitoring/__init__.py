from dependency_injector.wiring import Provide, inject
import logging
import os
import time as native_time
from threading import Lock, Thread


class WatchdogTimer:
    def __init__(self, timeout: float):
        self._timeout = timeout
        self._parent = None
        self._last_reset = None
        self._expiration = None
        self.alarmed = False

    def _alarm(self):
        self.alarmed = True

    def _tick(self, now: float):
        if self._expiration is not None:
            if now > self._expiration:
                self._alarm()
                # Prevent multiple alarms, but allow a reset to resume alarms
                self._expiration = None

    def reset(self):
        # noinspection PyProtectedMember
        with self._parent._lock:
            self._last_reset = native_time.monotonic()
            self._expiration = self._last_reset + self._timeout
            self.alarmed = False


class WatchdogLogTimer(WatchdogTimer):
    def __init__(self, timeout: float, log_level: int, name: str, extra):
        super().__init__(timeout)
        self._log_level = log_level
        self._name = name
        self._extra = extra

    def _alarm(self):
        self.alarmed = True
        logger = logging.getLogger(self._name)
        logger.log(
            self._log_level,
            f"Watchdog timer exceeded {self._timeout} seconds.",
            extra={"timeout": self._timeout, **self._extra},
        )


class Watchdog:

    _POLL_INTERVAL = 0.1

    @inject
    def __init__(self, config: dict = Provide["config"]):
        self._running = False
        self._timers = []
        self._lock = Lock()
        watchdog_config = config.get("watchdog")
        if watchdog_config is None:
            self._enabled = True
            self._poll_interval = self._POLL_INTERVAL
            self._liveness_file_name = ""
        else:
            self._enabled = watchdog_config.get("enabled", True)
            self._poll_interval = watchdog_config.get(
                "poll_interval", self._POLL_INTERVAL
            )
            self._liveness_file_name = watchdog_config.get("liveness_file_name", "")

    def add_timer(self, timer: WatchdogTimer):
        with self._lock:
            timer._parent = self
            self._timers.append(timer)
            if self._enabled and (not self._running):
                new_thread = Thread(target=self._run)
                new_thread.start()

    def remove_timer(self, timer: WatchdogTimer) -> None:
        with self._lock:
            self._timers.remove(timer)

    def _add_liveness_indicator(self):
        if len(self._liveness_file_name) > 0:
            if not os.path.exists(self._liveness_file_name):
                open(self._liveness_file_name, "a").close()

    def _run(self):
        try:
            while self._enabled:
                with self._lock:
                    self._running = True
                    if len(self._timers) > 0:
                        now = native_time.monotonic()
                        all_alive = True
                        for timer in self._timers:
                            # noinspection PyProtectedMember
                            timer._tick(now)
                            all_alive &= not timer.alarmed
                        if all_alive:
                            self._add_liveness_indicator()
                    else:
                        self._running = False
                        break
                native_time.sleep(self._poll_interval)
        except Exception as watchdog_exception:
            logging.critical(
                f"Unhandled exception: {watchdog_exception}", exc_info=True
            )
