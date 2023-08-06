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
from collections import defaultdict
from typing import Set

from wikivents.factories import Factory, MessageHandler, LoggingMessageHandler
from wikivents.ontology.wikidata import WikidataOntologyRepository
from wikivents.models import Entity, EntityId, ISO6391LanguageCode, Event, Resource, ParticipatingEntity
from wikivents.ontology import EventData
from wikivents.resource.exc import ResourceInLanguageDoesNotExist
from wikivents.resource.wikipedia import WikipediaResourceRepository


class WikimediaFactory(Factory):

    __DEFAULT_LANGUAGES = frozenset(
        [
            ISO6391LanguageCode("en"),
            ISO6391LanguageCode("fr"),
            ISO6391LanguageCode("de"),
            ISO6391LanguageCode("it"),
            ISO6391LanguageCode("es"),
        ]
    )

    repository = WikidataOntologyRepository()
    resources_repositories = dict()

    @staticmethod
    def get_instance() -> "Factory":
        return WikimediaFactory()

    @classmethod
    def create_entity(cls, entity_id: EntityId) -> Entity:
        return Entity(cls.repository.get_entity_data_from_id(entity_id))

    @classmethod
    def create_event(cls, event_id: EntityId, message_handler: MessageHandler = None) -> Event:
        event_data = cls.repository.get_event_data_from_id(event_id)
        message_handler = message_handler or LoggingMessageHandler()
        message_handler.add_number_of_steps(3)

        message_handler.info("Retrieving entity data from the repository")
        languages = cls.repository.get_official_languages_spoken_where_event_happened(event_data.id)
        cls.__initialize_resource_repositories(languages)

        message_handler.info("Retrieving connected entity resources to get more information about the event")
        resources = cls.__get_event_resources(event_data, languages)
        message_handler.add_number_of_steps(len(resources))
        message_handler.debug(f"There are {len(resources)} resources found for the event ‘{event_data.id}’.")

        entity = Entity(event_data, resources)

        message_handler.info("Retrieving event participants")
        participants = cls.__get_event_participants(resources, message_handler)
        message_handler.info(f"There are {len(participants)} participants found for this event")

        try:
            event_start_date = event_data.start_date
        except ValueError:
            event_start_date = None

        try:
            event_end_date = event_data.end_date
        except ValueError:
            event_end_date = None

        entity_places = cls.__get_event_places(event_data)
        return Event(entity, (event_start_date, event_end_date), participants, entity_places)

    @classmethod
    def __initialize_resource_repositories(cls, spoken_languages_iso_639_1_codes: Set[ISO6391LanguageCode]):
        for spoken_language_iso_639_1_code in spoken_languages_iso_639_1_codes | cls.__DEFAULT_LANGUAGES:
            try:
                if spoken_language_iso_639_1_code not in cls.resources_repositories:
                    cls.resources_repositories[
                        ISO6391LanguageCode(spoken_language_iso_639_1_code)
                    ] = WikipediaResourceRepository(spoken_language_iso_639_1_code, cls.repository)
            except ResourceInLanguageDoesNotExist:
                pass

    @classmethod
    def __get_event_places(cls, event_data: EventData) -> Set[Entity]:
        places = set()
        for event_place_id in event_data.places:
            places.add(cls.create_entity(event_place_id))
        return places

    @classmethod
    def __get_event_resources(
        cls, event_data: EventData, spoken_languages_iso_639_1_codes: Set[ISO6391LanguageCode]
    ) -> Set[Resource]:
        resources = set()
        site_links = event_data.resource_names
        for spoken_language_iso_639_1_code in spoken_languages_iso_639_1_codes | cls.__DEFAULT_LANGUAGES:
            wiki_language = ISO6391LanguageCode(f"{spoken_language_iso_639_1_code}wiki")
            if wiki_language in site_links:
                resources.add(
                    cls.resources_repositories.get(spoken_language_iso_639_1_code).get_resource_from_label(
                        site_links[wiki_language]
                    )
                )
        return resources

    @classmethod
    def __get_event_participants(cls, resources: Set[Resource], logger: MessageHandler) -> Set[ParticipatingEntity]:
        participating_entities_with_duplicates = set()
        for resource in resources:
            logger.info(f"Retrieving participating entities for resource ’{resource}’.")
            participating_entities_with_duplicates.update(
                cls.resources_repositories[resource.iso_639_1_language()].get_participating_entities_count_by_language(
                    resource
                )
            )
            logger.debug(
                f"There are now {len(participating_entities_with_duplicates)} entities " f"participating in the event"
            )

        participating_entities_found_in_languages = defaultdict(set)
        for participating_entity in participating_entities_with_duplicates:
            entity = participating_entity.entity
            participating_entities_found_in_languages[entity].add(participating_entity.language)

        participating_entities = set()
        for (
            entity,
            entity_language_list,
        ) in participating_entities_found_in_languages.items():
            participating_entities.add(ParticipatingEntity(entity, len(entity_language_list)))

        return participating_entities
