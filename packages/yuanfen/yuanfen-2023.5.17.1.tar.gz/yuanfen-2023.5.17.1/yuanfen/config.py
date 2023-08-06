import configparser
import json
import os
import threading

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from watchdog.observers import Observer

from . import logger


class Config:
    observer = None
    observer_lock = threading.Lock()

    def __init__(self, path, poll=True):
        self._path = path
        self._data = {}
        self._load()

        with Config.observer_lock:
            if Config.observer is None:
                Config.observer = PollingObserver() if poll else Observer()
                Config.observer.start()

            self.observer = Config.observer
            self.observer.schedule(ConfigChangeHandler(self), os.path.dirname(path), recursive=False)

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            return None

    def _load(self):
        with open(self._path, "r") as f:
            if self._path.endswith(".json"):
                self._data = json.load(f)
            elif self._path.endswith(".yaml") or self._path.endswith(".yml"):
                self._data = yaml.safe_load(f)
            elif self._path.endswith(".ini"):
                parser = configparser.ConfigParser()
                parser.read_file(f)
                for section in parser.sections():
                    self._data[section] = {}
                    for key, value in parser.items(section):
                        self._data[section][key] = value
            else:
                raise ValueError("Unsupported config file format")


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(self.config._path):
            self.config._load()
            logger.info(f"{event.src_path} reloaded")
