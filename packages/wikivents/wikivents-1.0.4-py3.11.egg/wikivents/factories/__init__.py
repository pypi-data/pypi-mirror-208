#!/usr/bin/env python3
#
# Copyright (C) 2020 Guillaume Bernard <contact@guillaume-bernard.fr>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import abc
import logging
from typing import Callable

from progress.bar import IncrementalBar

from wikivents.models import EntityId, Entity, Event


class Factory(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def create_entity(cls, entity_id: EntityId) -> Entity:
        pass

    @classmethod
    @abc.abstractmethod
    def create_event(cls, event_id: EntityId, message_handler: "MessageHandler" = None) -> Event:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_instance() -> "Factory":
        pass


class MessageHandler(abc.ABC):
    @property
    def number_of_steps(self) -> int:
        return self._number_of_steps

    def add_number_of_steps(self, number_of_steps: int):
        if number_of_steps > 0:
            self._number_of_steps += number_of_steps

    def __init__(self):
        self._number_of_steps = 0
        self._step_process_number = 0

    @abc.abstractmethod
    def info(self, message: str):
        pass

    @abc.abstractmethod
    def debug(self, message: str):
        pass


class LoggingMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s in %(module)s − %(message)s")
        )
        self._logger.addHandler(console_handler)
        self._logger.setLevel(logging.DEBUG)

    def info(self, message: str):
        self._logger.info("%s: %d/%d", message, self._step_process_number, self._number_of_steps)
        self._step_process_number += 1

    def debug(self, message: str):
        self._logger.debug("%s: %d/%d", message, self._step_process_number, self._number_of_steps)


class CallbackMessageHandler(MessageHandler):
    def __init__(self, callback: Callable[[str, int, int], None] = lambda *args, **kwargs: None):
        super().__init__()
        self._callback = callback

    def info(self, message: str):
        self._callback(message, self._step_process_number, self._number_of_steps)
        self._step_process_number += 1

    def debug(self, message: str):
        pass


class LoggingCallbackMessageHandler(LoggingMessageHandler, CallbackMessageHandler):
    def __init__(self, callback: Callable[[str, int, int], None] = lambda *args, **kwargs: None):
        LoggingMessageHandler.__init__(self)
        CallbackMessageHandler.__init__(self, callback)

    def info(self, message: str):
        self._callback(message, self._step_process_number, self._number_of_steps)
        self._logger.info("%s: %d/%d", message, self._step_process_number, self._number_of_steps)
        self._step_process_number += 1

    def debug(self, message: str):
        self._logger.debug("%s: %d/%d", message, self._step_process_number, self._number_of_steps)


class ProgressBarHandler(MessageHandler):
    def __init__(self):
        super().__init__()
        self._bar = IncrementalBar("Event definition progress", max=self.number_of_steps, suffix="%(percent)d%%")

    def info(self, message: str):
        self._bar.max = self.number_of_steps
        self._bar.next()

    def debug(self, message: str):
        pass
