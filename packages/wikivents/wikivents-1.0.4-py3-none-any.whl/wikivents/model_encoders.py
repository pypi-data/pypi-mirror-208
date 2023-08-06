#!/usr/bin/env python3
#
# Copyright (C) 2021 Guillaume Bernard <contact@guillaume-bernard.fr>
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
from typing import Dict, Any

from wikivents.models import ParticipatingEntity, ISO6391LanguageCode, EntityType, Event


class EventEncoder(abc.ABC):
    def __init__(self, event: Event, iso_639_1_language_code: ISO6391LanguageCode):
        self.event = event
        self.iso_639_1_language_code = iso_639_1_language_code

    @abc.abstractmethod
    def encode(self, keep_entities_if_present_in_at_least_x_languages: int = 2) -> Dict[str, Dict[str, Any]]:
        pass

    def _get_start_date_or_empty(self) -> str:
        try:
            beginning = self.event.beginning.isoformat()
        except ValueError:
            beginning = str()
        return beginning

    def _get_end_date_or_empty(self) -> str:
        try:
            end = self.event.end.isoformat()
        except ValueError:
            end = str()
        return end


class EventToDictEncoder(EventEncoder):
    def encode(self, keep_entities_if_present_in_at_least_x_languages: int = 2) -> Dict[str, Dict[str, Any]]:
        return {
            self.event.id: {
                "iso_639_1_language_code": self.iso_639_1_language_code,
                "id": self.event.id,
                "type": EntityType.EVENT.name,
                "label": self.event.label(self.iso_639_1_language_code),
                "description": self.event.description(self.iso_639_1_language_code),
                "names": list(self.event.names(self.iso_639_1_language_code)),
                "processed_languages": list(self.event.processed_languages_iso_639_1_codes),
                "entities_kept_if_in_more_than_X_languages": keep_entities_if_present_in_at_least_x_languages,
                "start": self._get_start_date_or_empty(),
                "end": self._get_end_date_or_empty(),
                "entities": {
                    "per": [
                        self.__get_participating_dict(participating_per, self.iso_639_1_language_code)
                        for participating_per in self.event.entities(
                            EntityType.PERSON,
                            keep_entities_if_present_in_at_least_x_languages,
                        )
                    ],
                    "gpe": [
                        self.__get_participating_dict(participating_gpe, self.iso_639_1_language_code)
                        for participating_gpe in self.event.entities(
                            EntityType.GPE,
                            keep_entities_if_present_in_at_least_x_languages,
                        )
                    ],
                    "org": [
                        self.__get_participating_dict(participating_org, self.iso_639_1_language_code)
                        for participating_org in self.event.entities(
                            EntityType.ORG,
                            keep_entities_if_present_in_at_least_x_languages,
                        )
                    ],
                },
            }
        }

    # pylint: disable=no-self-use
    # noinspection PyMethodMayBeStatic
    def __get_participating_dict(
        self, participating_entity: ParticipatingEntity, iso_639_1_language_code: ISO6391LanguageCode
    ) -> Dict[str, Any]:
        return {
            "id": participating_entity.entity.id,
            "type": [entity_type.name for entity_type in participating_entity.entity.types()],
            "label": participating_entity.entity.label(iso_639_1_language_code),
            "description": participating_entity.entity.label(iso_639_1_language_code),
            "names": list(participating_entity.entity.names(iso_639_1_language_code)),
            "count": participating_entity.count,
        }
