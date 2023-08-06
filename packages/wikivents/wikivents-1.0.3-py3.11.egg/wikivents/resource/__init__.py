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
from typing import Set

from wikivents.models import ParticipatingEntity, Resource


class EntityResourceRepository(abc.ABC):
    @abc.abstractmethod
    def get_resource_from_label(self, label: str) -> Resource:
        pass

    @abc.abstractmethod
    def get_participating_entities_count_by_language(self, resource: Resource) -> Set[ParticipatingEntity]:
        pass


class EntityResourceCache(EntityResourceRepository, abc.ABC):
    @abc.abstractmethod
    def set_resource_from_label(self, label: str, resource: Resource):
        pass

    @abc.abstractmethod
    def set_participating_entities(self, resource: Resource, participating_entities: Set[ParticipatingEntity]):
        pass


class EntityResourceAPI(EntityResourceRepository, abc.ABC):
    pass
