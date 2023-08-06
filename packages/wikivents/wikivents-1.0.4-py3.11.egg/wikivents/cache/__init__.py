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
import shutil
from pathlib import Path
from typing import Any, List, Tuple

# The security risk is taken into account, this means ignored.
import dill  # nosec

from wikivents.exc import NotInCacheException


class AbstractCachePath(abc.ABC):
    @abc.abstractmethod
    def get_filepath(self, path_directories_and_filename: Tuple[str]) -> Path:
        pass

    @abc.abstractmethod
    def expire(self):
        pass


class CachePath(AbstractCachePath):
    def __init__(self, specific_cache_directory_name: str, suffix: str):
        self.__base_path = Path.home().joinpath(".cache", "wikivents", specific_cache_directory_name)
        self.__suffix = suffix
        if self.__base_path.exists():
            self.__base_path.mkdir(parents=True, exist_ok=True)

    def get_filepath(self, path_directories_and_filename: List[str]) -> Path:
        file_path = self.__base_path.joinpath(*path_directories_and_filename)
        file_path.parents[0].mkdir(parents=True, exist_ok=True)
        return file_path.with_suffix(self.__suffix)

    def expire(self):
        shutil.rmtree(self.__base_path)


class Cache(abc.ABC):
    @abc.abstractmethod
    def _get_data_else_raise_exception(self, data_identifiers: List[str]) -> Any:
        pass

    @abc.abstractmethod
    def _set_data(self, data_identifiers: List[str], data: Any):
        pass


class DillCache(Cache):
    def __init__(self, specific_cache_directory_name: str):
        self.__cache_path = CachePath(specific_cache_directory_name, ".dill")

    def _get_data_else_raise_exception(self, data_identifiers: List[str]) -> Any:
        input_path_file = self.__cache_path.get_filepath(data_identifiers)
        if input_path_file.exists():
            with open(input_path_file, mode="rb") as input_file:
                return dill.load(input_file)  # nosec
        raise NotInCacheException(f"There is not caching file for {input_path_file}")

    def _set_data(self, data_identifiers: List[str], data: Any):
        with open(self.__cache_path.get_filepath(data_identifiers), mode="wb") as output_file:
            dill.dump(data, output_file)  # nosec
