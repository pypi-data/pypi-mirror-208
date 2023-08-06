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
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType, Set, Tuple, Dict, Iterator, List

from wikivents.exc import EntityIsNotAnEventError

ISO6391LanguageCode = NewType("ISO6391LanguageCode", str)
EntityId = NewType("EntityId", str)
PropertyId = NewType("PropertyId", str)

DEFAULT_LANGUAGE = ISO6391LanguageCode("en")


class EntityType(Enum):
    PERSON = {"Q5"}  # Human
    ORG = {
        "Q43229",  # Organisation
        "Q4164871",  # Position
    }
    GPE = {
        "Q3257686",  # Locality
        "Q6256",  # Country
        "Q56061",  # Territorial Entity
    }
    EVENT = {"Q1190554", "Q1656682"}  # Occurrence  # Event
    UNKNOWN = set()

    @staticmethod
    def get_types(entity_id_set: Set[EntityId]) -> Set["EntityType"]:
        """
        :param entity_id_set: the set of Entity ids which all define the same EntityType. For instance {"Q1190554"},
                              {"Q1656682"} or {"Q1190554", "Q1656682"} are EntityType.OCCURRENCE.

        """
        return {entity_type for entity_type in EntityType if entity_type.value.intersection(entity_id_set)}

    def __str__(self) -> str:
        return str(self.name)


class SingleValueMultilingualText(collections.abc.Mapping):
    @abc.abstractmethod
    def __getitem__(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        """Get the single value associated with the input language code"""

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class MultipleValuesMultilingualText(collections.abc.Mapping):
    @abc.abstractmethod
    def __getitem__(self, iso_639_1_language_code: ISO6391LanguageCode) -> Set[str]:
        """Get the multiple values associated with the input language code"""

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class SingleValueMultiLingualTextFromDict(SingleValueMultilingualText):
    def __init__(self, multiple_values_dict: Dict[ISO6391LanguageCode, str]):
        self.__multiple_values_dict = multiple_values_dict

    def __getitem__(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        return self.__multiple_values_dict.get(iso_639_1_language_code, str())

    def __len__(self) -> int:
        return len(self.__multiple_values_dict)

    def __iter__(self) -> Iterator[ISO6391LanguageCode]:
        for iso_639_1_language_code in self.__multiple_values_dict:
            yield iso_639_1_language_code

    def __contains__(self, item) -> bool:
        return item in self.__multiple_values_dict.keys()

    def __str__(self) -> str:
        if ISO6391LanguageCode(DEFAULT_LANGUAGE) in self.__multiple_values_dict:
            return self.__multiple_values_dict.get(ISO6391LanguageCode(DEFAULT_LANGUAGE))
        if len(self.__multiple_values_dict) > 0:
            return next(iter(self.__multiple_values_dict))
        return "SingleValueMultiLingualTextFromDict()"


class MultipleValuesMultiLingualTextFromDict(MultipleValuesMultilingualText):
    def __init__(self, multiple_values_dict: Dict[ISO6391LanguageCode, Set[str]]):
        self.__multiple_values_dict = multiple_values_dict

    def __getitem__(self, iso_639_1_language_code: ISO6391LanguageCode) -> Set[str]:
        return self.__multiple_values_dict.get(iso_639_1_language_code, set())

    def __len__(self) -> int:
        return len(self.__multiple_values_dict)

    def __iter__(self) -> Iterator[ISO6391LanguageCode]:
        for iso_639_1_language_code in self.__multiple_values_dict:
            yield iso_639_1_language_code

    def __contains__(self, item) -> bool:
        return item in self.__multiple_values_dict.keys()

    def __str__(self) -> str:
        if ISO6391LanguageCode(DEFAULT_LANGUAGE) in self.__multiple_values_dict:
            return repr(self.__multiple_values_dict.get(ISO6391LanguageCode(DEFAULT_LANGUAGE)))
        if len(self.__multiple_values_dict) > 0:
            return next(iter(self.__multiple_values_dict))
        return "MultipleValuesMultiLingualTextFromDict()"


class Resource(abc.ABC):
    @abc.abstractmethod
    def content(self) -> str:
        pass

    @abc.abstractmethod
    def entities(self) -> Dict[str, int]:
        pass

    @abc.abstractmethod
    def iso_639_1_language(self) -> ISO6391LanguageCode:
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass


class InformativeEntity(abc.ABC):

    # pylint: disable=invalid-name
    @property
    def id(self):
        pass

    @abc.abstractmethod
    def label(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        pass

    @abc.abstractmethod
    def names(self, iso_639_1_language_code: ISO6391LanguageCode) -> Set[str]:
        pass

    @abc.abstractmethod
    def description(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        pass

    @abc.abstractmethod
    def types(self) -> Set[EntityType]:
        pass

    @abc.abstractmethod
    def types_as_entities(self) -> Set["Entity"]:
        pass

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return f"<{self.__class__.__name__}({self.id}, {self.label(ISO6391LanguageCode(DEFAULT_LANGUAGE))})>"

    def __hash__(self):
        return hash(self.id)


class Entity(InformativeEntity):
    def __init__(self, entity_data: "EntityData", resources: Set[Resource] = None):  # noqa: F821
        self.__id = entity_data.id
        self.__types = EntityType.get_types(entity_data.hierarchical_instance_of_ids)
        self.__types_entities = {Entity(type_entity_data) for type_entity_data in entity_data.instance_of}
        self.__label = entity_data.labels
        self.__description = entity_data.descriptions
        self.__names = entity_data.names
        self.__resources = resources or set()

    # pylint: disable=invalid-name
    @property
    def id(self):
        return self.__id

    def label(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        return self.__label.get(iso_639_1_language_code)

    def names(self, iso_639_1_language_code: ISO6391LanguageCode) -> Set[str]:
        return self.__names.get(iso_639_1_language_code)

    def description(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        return self.__description.get(iso_639_1_language_code)

    def types(self) -> Set[EntityType]:
        return self.__types

    def types_as_entities(self) -> Set["Entity"]:
        return self.__types_entities

    def resources(self) -> Set[Resource]:
        return self.__resources

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return f"<{self.__class__.__name__}({self.id}, {self.label(ISO6391LanguageCode(DEFAULT_LANGUAGE))})>"

    def __hash__(self):
        return hash(f"entity_{self.id}")


@dataclass(eq=True, unsafe_hash=True, frozen=True)
class ParticipatingEntity:
    entity: Entity
    count: int


@dataclass(eq=True, unsafe_hash=True, frozen=True)
class EntityCountByLanguage(ParticipatingEntity):
    language: ISO6391LanguageCode


class Event(InformativeEntity):
    @property
    def gpe(self) -> List[ParticipatingEntity]:
        return self.entities(EntityType.GPE, 1)

    @property
    def org(self) -> List[ParticipatingEntity]:
        return self.entities(EntityType.ORG, 1)

    @property
    def per(self) -> List[ParticipatingEntity]:
        return self.entities(EntityType.PERSON, 1)

    @property
    def nb_of_processed_languages(self) -> int:
        return len(self.__entity.resources())

    @property
    def beginning(self) -> datetime.date:
        if self.__start_date:
            return self.__start_date
        raise ValueError(f"There is no known starting date for event {self.label(DEFAULT_LANGUAGE)}")

    @property
    def end(self) -> datetime.date:
        if self.__end_date:
            return self.__end_date
        raise ValueError(f"There is no known end date for event {self.label(DEFAULT_LANGUAGE)}")

    @property
    def processed_languages_iso_639_1_codes(self) -> Set[str]:
        return {resource.iso_639_1_language() for resource in self.__entity.resources()}

    def __init__(
        self,
        entity: Entity,
        dates: Tuple[datetime, datetime],
        participants: Set[ParticipatingEntity],
        places: Set[Entity],
    ):
        if EntityType.EVENT not in entity.types():
            raise EntityIsNotAnEventError(
                "The entity given to initialise the event is not declared as an event for Wikidata."
            )
        self.__entity = entity
        self.__participants = participants
        self.__places = places
        self.__start_date, self.__end_date = dates

    # pylint: disable=invalid-name
    @property
    def id(self) -> str:
        return self.__entity.id

    def label(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        return self.__entity.label(iso_639_1_language_code)

    def names(self, iso_639_1_language_code: ISO6391LanguageCode) -> Set[str]:
        return self.__entity.names(iso_639_1_language_code)

    def description(self, iso_639_1_language_code: ISO6391LanguageCode) -> str:
        return self.__entity.description(iso_639_1_language_code)

    def places(self) -> Set[Entity]:
        return self.__places

    def types(self) -> Set[EntityType]:
        return self.__entity.types()

    def types_as_entities(self) -> Set["Entity"]:
        return self.__entity.types_as_entities()

    def participants(self) -> Set[ParticipatingEntity]:
        return self.__participants

    def entities(
        self, entity_type: EntityType, keep_if_participating_entity_in_at_least_x_languages: int = 1
    ) -> List[ParticipatingEntity]:
        participating_entities = {
            participating_entity
            for participating_entity in self.__participants
            if (
                entity_type in participating_entity.entity.types()
                and participating_entity.count >= keep_if_participating_entity_in_at_least_x_languages
            )
        }
        return sorted(
            participating_entities, key=lambda participating_entity: participating_entity.count, reverse=True
        )

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.__class__.__name__}({self.id}, {self.label(ISO6391LanguageCode(DEFAULT_LANGUAGE))})>"

    def __hash__(self):
        return hash(f"event_{self.id}")
