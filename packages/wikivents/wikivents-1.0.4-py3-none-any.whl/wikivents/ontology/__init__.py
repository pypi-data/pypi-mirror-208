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
import collections.abc
from datetime import datetime
from typing import Set, Dict, Iterator, List

from wikivents.models import (
    EntityId,
    ISO6391LanguageCode,
    SingleValueMultilingualText,
    MultipleValuesMultilingualText,
    PropertyId,
)


class EntityData(collections.abc.Mapping):

    # pylint: disable=invalid-name
    @property
    @abc.abstractmethod
    def id(self) -> EntityId:
        pass

    @property
    @abc.abstractmethod
    def uri(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def labels(self) -> SingleValueMultilingualText:
        pass

    @property
    @abc.abstractmethod
    def descriptions(self) -> SingleValueMultilingualText:
        pass

    @property
    @abc.abstractmethod
    def names(self) -> MultipleValuesMultilingualText:
        pass

    @property
    @abc.abstractmethod
    def resource_names(self) -> Dict[ISO6391LanguageCode, str]:
        pass

    @property
    @abc.abstractmethod
    def aliases(self) -> Set[str]:
        pass

    @property
    @abc.abstractmethod
    def instance_of_ids(self) -> Set[EntityId]:
        pass

    @property
    @abc.abstractmethod
    def hierarchical_instance_of_ids(self) -> Set[EntityId]:
        pass

    @hierarchical_instance_of_ids.setter
    @abc.abstractmethod
    def hierarchical_instance_of_ids(self, set_of_types_ids: Set[EntityId]):
        pass

    @property
    @abc.abstractmethod
    def instance_of(self) -> Set["EntityData"]:
        pass

    @instance_of.setter
    @abc.abstractmethod
    def instance_of(self, instance_of_entities_data: Set["EntityData"]):
        pass

    @abc.abstractmethod
    def __getitem__(self, item) -> List[Dict[str, str]]:
        pass

    @abc.abstractmethod
    def __iter__(self) -> Iterator[PropertyId]:
        pass

    @abc.abstractmethod
    def __contains__(self, item) -> bool:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    @abc.abstractmethod
    def __hash__(self) -> int:
        pass


# pylint: disable=too-many-ancestors
class EventData(EntityData, abc.ABC):
    @property
    @abc.abstractmethod
    def start_date(self) -> datetime.date:
        pass

    @property
    @abc.abstractmethod
    def end_date(self) -> datetime.date:
        pass

    @property
    @abc.abstractmethod
    def places(self) -> Set[EntityId]:
        pass


class EntityOntologyRepository(abc.ABC):
    @abc.abstractmethod
    def get_entity_data_from_id(self, entity_id: EntityId) -> EntityData:
        pass

    @abc.abstractmethod
    def get_event_data_from_id(self, event_id: EntityId) -> EventData:
        pass

    @abc.abstractmethod
    def is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId) -> bool:
        pass

    @abc.abstractmethod
    def get_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId) -> Set[EntityId]:
        pass

    @abc.abstractmethod
    def get_official_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        pass

    @abc.abstractmethod
    def get_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        pass


class EntityOntologyCache(EntityOntologyRepository, abc.ABC):
    @abc.abstractmethod
    def set_entity_data_from_id(self, entity_id: EntityId, entity_data: EntityData):
        pass

    @abc.abstractmethod
    def set_event_data_from_id(self, event_id: EntityId, event_data: EventData):
        pass

    @abc.abstractmethod
    def set_is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId, is_instance: bool):
        pass

    @abc.abstractmethod
    def set_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId, entities: Set[EntityId]):
        pass

    @abc.abstractmethod
    def set_official_languages_spoken_where_event_happened(
        self, event_id: EntityId, official_languages: Set[ISO6391LanguageCode]
    ):
        pass

    @abc.abstractmethod
    def set_languages_spoken_where_event_happened(
        self, event_id: EntityId, spoken_languages: Set[ISO6391LanguageCode]
    ):
        pass


class EntityOntologyAPI(EntityOntologyRepository, abc.ABC):
    pass
