#!/usr/bin/env python3
#
# Copyright (C) 2020-2021 Guillaume Bernard <contact@guillaume-bernard.fr>
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
from datetime import datetime, timedelta
from threading import Lock
from typing import Set, Any, Mapping, Dict, List, Iterator

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from wikidata.entity import EntityId as WikidataEntityId

from wikivents.cache import DillCache
from wikivents.exc import NotInCacheException
from wikivents.models import (
    EntityId,
    ISO6391LanguageCode,
    SingleValueMultilingualText,
    SingleValueMultiLingualTextFromDict,
    MultipleValuesMultiLingualTextFromDict,
    MultipleValuesMultilingualText,
    PropertyId,
    EntityType,
)
from wikivents.ontology import EntityOntologyAPI, EntityOntologyCache, EntityOntologyRepository, EntityData, EventData
from wikivents.ontology.exc import EntityDataDoesNotMatchAnEventError


class WikidataEntityData(EntityData):
    __ID_OF_INSTANCE_OF_HIERARCHICAL = "P31-hierarchical"

    def __init__(self, wikidata_api_data: Mapping[str, Any]):
        self.__wikidata_api_data = wikidata_api_data
        self.__claims = wikidata_api_data.get("claims")
        self.__instance_of_entities_data = set()
        if self.__ID_OF_INSTANCE_OF_HIERARCHICAL not in self.__claims:
            self.__claims[self.__ID_OF_INSTANCE_OF_HIERARCHICAL] = list()

    @property
    def id(self) -> EntityId:
        return EntityId(self.__wikidata_api_data.get("id"))

    @property
    def uri(self) -> str:
        return f"https://www.wikidata.org/wiki/{self.id}"

    @property
    def labels(self) -> SingleValueMultilingualText:
        return SingleValueMultiLingualTextFromDict(
            self._get_language_representation(self.__wikidata_api_data.get("labels"))
        )

    @property
    def descriptions(self) -> SingleValueMultilingualText:
        return SingleValueMultiLingualTextFromDict(
            self._get_language_representation(self.__wikidata_api_data.get("descriptions"))
        )

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def _get_language_representation(self, entity_data_language: Mapping[str, Any]) -> Dict[ISO6391LanguageCode, str]:
        return {
            ISO6391LanguageCode(iso_639_1_language_code): language_value_dict.get("value")
            for iso_639_1_language_code, language_value_dict in entity_data_language.items()
        }

    @property
    def names(self) -> MultipleValuesMultilingualText:
        """
        The different names that the entity has and is known by. Alternative names are the entity label, the Wikipedia
        page name linked to the entity and the alternative names registered in the Wikidata entity page.

        :return: the different names that are used, in the targeted language, to describe the entity.
        """
        names = defaultdict(set)

        for iso_639_1_language_code, label in self.labels.items():
            names[iso_639_1_language_code].add(label)

        for iso_639_1_language_code, site_link in self.resource_names.items():
            names[iso_639_1_language_code].add(site_link)

        for iso_639_1_language_code, aliases in self.aliases.items():
            names[iso_639_1_language_code].update(aliases)

        return MultipleValuesMultiLingualTextFromDict(names)

    @property
    def resource_names(self) -> Dict[ISO6391LanguageCode, str]:
        return {
            ISO6391LanguageCode(iso_639_1_language_code): language_value_dict.get("title")
            for iso_639_1_language_code, language_value_dict in self.__wikidata_api_data.get(
                "sitelinks", dict()
            ).items()
        }

    @property
    def aliases(self) -> Dict[ISO6391LanguageCode, List[str]]:
        return {
            ISO6391LanguageCode(iso_639_1_language_code): [item.get("value") for item in language_value_list]
            for iso_639_1_language_code, language_value_list in self.__wikidata_api_data.get("aliases", dict()).items()
        }

    @property
    def instance_of_ids(self) -> Set[EntityId]:
        return {
            entity_type_dict.get("mainsnak").get("datavalue").get("value").get("id")
            for entity_type_dict in self.__claims.get("P31", dict())
        }

    @property
    def hierarchical_instance_of_ids(self) -> Set[EntityId]:
        return {
            entity_type_dict.get("mainsnak").get("datavalue").get("value").get("id")
            for entity_type_dict in self.__claims.get(self.__ID_OF_INSTANCE_OF_HIERARCHICAL, list())
        } | self.instance_of_ids

    @hierarchical_instance_of_ids.setter
    def hierarchical_instance_of_ids(self, set_of_types_ids: Set[EntityId]):
        for entity_id in set_of_types_ids:
            self.__claims[self.__ID_OF_INSTANCE_OF_HIERARCHICAL].append(
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "numeric-id": entity_id[1:], "id": entity_id},
                            "type": "wikibase-entityid",
                        },
                    }
                }
            )

    @property
    def instance_of(self) -> Set["EntityData"]:
        return self.__instance_of_entities_data

    @instance_of.setter
    def instance_of(self, instance_of_entities_data: Set["EntityData"]):
        instance_of_ids = self.instance_of_ids
        self.__instance_of_entities_data = {
            instance_of_entity_data
            for instance_of_entity_data in instance_of_entities_data
            if instance_of_entity_data.id in instance_of_ids
        }

    def __getitem__(self, property_id: PropertyId) -> List[Dict[str, str]]:
        return [
            property_value.get("mainsnak").get("datavalue").get("value")
            for property_value in self.__claims.get(property_id, dict())
        ]

    def __iter__(self) -> Iterator[PropertyId]:
        for property_id in self.__claims:
            yield property_id

    def __contains__(self, item) -> bool:
        return item in self.__wikidata_api_data.keys()

    def __len__(self) -> int:
        return len(self.__wikidata_api_data)

    def __hash__(self) -> int:
        return hash(self.id)


# pylint: disable=too-many-ancestors
class WikidataEventData(EventData):
    def __init__(self, entity_data: EntityData):
        self.__entity_data = entity_data
        if not self.__entity_data.hierarchical_instance_of_ids & EntityType.EVENT.value:
            raise EntityDataDoesNotMatchAnEventError(
                f"The given entity data ({self.__entity_data.id}) given is not event data. They are not instances "
                f"of {EntityType.EVENT.value}. {self.__entity_data.hierarchical_instance_of_ids} instead."
            )

    @property
    def start_date(self) -> datetime.date:
        """
        Get the event date, and convert it, if necessary to a Gregorian date.

        The date given in Wikidata is given as Gregorian (https://www.wikidata.org/wiki/Q1985727) or
        as Julian (https://www.wikidata.org/wiki/Q1985786).
        """
        # https://www.wikidata.org/w/index.php?title=Special:ListProperties/time
        event_starting_dates, point_in_time, start_time = [], PropertyId("P580"), PropertyId("P585")
        for date_property in point_in_time, start_time:
            for wikidata_date_value in self.__entity_data.get(date_property) or []:
                event_starting_dates.append(
                    (wikidata_date_value.get("time"), EntityId(wikidata_date_value.get("calendarmodel")))
                )
        # TODO: select the most relevant date if multiple
        if len(event_starting_dates) > 0:
            return self.__get_datetime_from_wikidata_date_format(*event_starting_dates[0])
        raise ValueError("This entity does not provide any start time information")

    @property
    def end_date(self) -> datetime.date:
        event_ending_dates, end_time = [], PropertyId("P582")
        for wikidata_time_value in self.__entity_data.get(end_time) or []:
            event_ending_dates.append(
                (wikidata_time_value.get("time"), EntityId(wikidata_time_value.get("calendarmodel")))
            )
        # TODO: select the most relevant date if multiple
        if len(event_ending_dates) > 0:
            return self.__get_datetime_from_wikidata_date_format(*event_ending_dates[0])
        raise ValueError("This entity does not provide any end time information")

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_datetime_from_wikidata_date_format(
        self, wikidata_time_format: str, calendar_model: EntityId
    ) -> datetime.date:
        # https://www.wikidata.org/wiki/Help:Dates
        for date_format in [
            "+%Y-%m-%dT%H:%M:%S%z",  # day precision
            "+%Y-%m-00T%H:%M:%S%z",  # month precision
            "+%Y-00-00T%H:%M:%S%z",  # year precision
        ]:
            try:
                gregorian_date = original_date = datetime.strptime(wikidata_time_format, date_format)
            except ValueError:
                pass
            else:
                # Julian date that needs conversion to gregorian
                julian_calendar = EntityId("Q1985786")
                if julian_calendar in calendar_model:
                    # FIXME: AC and BC dates are not both supported.
                    # FIXME: Julian date to Gregorian is not appropriate
                    gregorian_date = original_date + timedelta(days=13)  # The delta in the 20th century
                return gregorian_date  # Keep only the first date

    @property
    def places(self) -> Set[EntityId]:
        places_ids, location, country = set(), PropertyId("P276"), PropertyId("P17")
        for location_property in location, country:
            for place in self.__entity_data.get(location_property) or []:
                places_ids.add(place.get("id"))
        return places_ids

    @property
    def id(self) -> EntityId:
        return self.__entity_data.id

    @property
    def uri(self) -> str:
        return self.__entity_data.uri

    @property
    def labels(self) -> SingleValueMultilingualText:
        return self.__entity_data.labels

    @property
    def descriptions(self) -> SingleValueMultilingualText:
        return self.__entity_data.descriptions

    @property
    def names(self) -> MultipleValuesMultilingualText:
        return self.__entity_data.names

    @property
    def resource_names(self) -> Dict[ISO6391LanguageCode, str]:
        return self.__entity_data.resource_names

    @property
    def aliases(self) -> Set[str]:
        return self.__entity_data.aliases

    @property
    def instance_of_ids(self) -> Set[EntityId]:
        return self.__entity_data.instance_of_ids

    @property
    def hierarchical_instance_of_ids(self) -> Set[EntityId]:
        return self.__entity_data.hierarchical_instance_of_ids

    @hierarchical_instance_of_ids.setter
    def hierarchical_instance_of_ids(self, set_of_types_ids: Set[EntityId]):
        self.__entity_data.hierarchical_instance_of_ids = set_of_types_ids

    @property
    def instance_of(self) -> Set["EntityData"]:
        return self.__entity_data.instance_of

    @instance_of.setter
    def instance_of(self, instance_of_entities_data: Set["EntityData"]):
        self.__entity_data.instance_of = instance_of_entities_data

    def __getitem__(self, item) -> List[Dict[str, str]]:
        return self.__entity_data.__getitem__(item)

    def __iter__(self) -> Iterator[PropertyId]:
        return self.__entity_data.__iter__()

    def __contains__(self, item) -> bool:
        return item in self.__entity_data

    def __len__(self) -> int:
        return len(self.__entity_data)

    def __hash__(self):
        return hash(self.__entity_data)


class _WikidataAPI(EntityOntologyAPI):
    user_agent = "Wikidata Python export/0.1 (https://gitlab.com/guilieb/wikivents)"
    endpoint_url = "https://query.wikidata.org/sparql"

    def __init__(self):
        self.__wikidata_client = Client()
        self.__sparql_wrapper = SPARQLWrapper(_WikidataAPI.endpoint_url, agent=_WikidataAPI.user_agent)
        self.__sparql_wrapper.setReturnFormat(JSON)

    def is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId) -> bool:
        """
        Check whether an entity id corresponds to an element which is an instance of another entity id.

        :param entity_id: the entity id of the entity to check
        :param instance_of_entity_id: the entity of the entity that represent the type that’s checked
        """
        self.__sparql_wrapper.setQuery(
            f"""ASK WHERE {{
                wd:%{entity_id} wdt:P31 ?instance_of.
                ?instance_of wdt:P279* ?mid.
                ?mid wdt:P279* ?element_classes.
                FILTER (wd:%{instance_of_entity_id} IN (?element_classes))
            }}"""
        )
        return bool(self.__sparql_wrapper.query().convert().get("boolean"))

    def get_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId) -> Set[EntityId]:
        """
        Get all instance_of values of the Entity represented by its identifier given in parameter

        :param entity_id: the element for which to get instance_of values.
        :return: the list of entity identifiers that the given entity is an instance of. For instance, for the event id
            Q193689 (Q193689 is “Easter Rising”), values are ['Q124734']. (Q124734 is “rebellion”)
        """
        self.__sparql_wrapper.setQuery(
            f"""SELECT ?element_class (COUNT(?mid) AS ?depth) WHERE {{
                wd:{entity_id} wdt:P31 ?instance_of.
                ?instance_of wdt:P279* ?mid.
                ?mid wdt:P279* ?element_class.
            }} GROUP BY ?element_class
            ORDER BY ?depth"""
        )
        return {
            element_class.get("element_class").get("value").split("/")[-1]
            for element_class in self.__sparql_wrapper.query().convert().get("results").get("bindings")
        }

    def get_entity_data_from_id(self, entity_id: EntityId) -> EntityData:
        wikidata_api_data = WikidataEntityData(self.__wikidata_client.get(WikidataEntityId(entity_id), load=True).data)
        wikidata_api_data.instance_of = {
            WikidataEntityData(self.__wikidata_client.get(WikidataEntityId(type_id), load=True).data)
            for type_id in wikidata_api_data.instance_of_ids
        }
        wikidata_api_data.hierarchical_instance_of_ids = self.get_all_entities_id_the_entity_is_an_instance_of(
            entity_id
        )
        return wikidata_api_data

    def get_event_data_from_id(self, event_id: EntityId) -> EventData:
        return WikidataEventData(self.get_entity_data_from_id(event_id))

    def get_official_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        self.__sparql_wrapper.setQuery(
            f"""
            SELECT DISTINCT ?language_code WHERE {{
              {{
                wd:{event_id} wdt:P17 ?country.
                ?country wdt:P37 ?official_language.
                ?official_language wdt:P424 ?language_code.
              }}
              UNION
              {{
                wd:{event_id} wdt:P17 ?country.
                ?country wdt:P37 ?official_language.
                ?official_language wdt:P4913 ?language_dialect.
                ?language_dialect wdt:P424 ?language_code.
              }}
            }}
        """
        )
        return self.__filter_only_existing_wikipedia_projects_from_language_codes(
            {
                ISO6391LanguageCode(language_codes_dict.get("language_code").get("value"))
                for language_codes_dict in self.__sparql_wrapper.query().convert().get("results").get("bindings")
            }
        )

    def get_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        self.__sparql_wrapper.setQuery(
            f"""
            SELECT DISTINCT ?language_code WHERE {{
              {{
                wd:{event_id} wdt:P17 ?country.
                ?country wdt:P37 | wdt:P2936 ?language.
                ?language wdt:P424 ?language_code.
              }}
            UNION
              {{
                wd:{event_id} wdt:P17 ?country.
                ?country wdt:P37 ?language.
                ?language wdt:P4913 ?language_dialect.
                ?language_dialect wdt:P424 ?language_code.
              }}
            }}
        """
        )
        return self.__filter_only_existing_wikipedia_projects_from_language_codes(
            {
                ISO6391LanguageCode(language_codes_dict.get("language_code").get("value"))
                for language_codes_dict in self.__sparql_wrapper.query().convert().get("results").get("bindings")
            }
        )

    # pylint: disable=no-self-use
    # noinspection PyMethodMayBeStatic
    def __filter_only_existing_wikipedia_projects_from_language_codes(
        self, iso_639_1_language_codes: Set[ISO6391LanguageCode]
    ):
        """
        Keep only, from a list of language codes, them with an associated Wikipedia version. For instance
        ‘fr’ has the https://fr.wikipedia.org, as well as ‘en’ with https://en.wikipedia.org while ‘en-us’
        does not have one, as https://en-us.wikipedia.org does not exist.
        """
        existing_wikipedia_projects_language_codes = set()
        for iso_639_1_language_code in iso_639_1_language_codes:
            try:
                response = requests.get(f"https://{iso_639_1_language_code}.wikipedia.org")
                if response.status_code == 200:
                    existing_wikipedia_projects_language_codes.add(iso_639_1_language_code)
            except requests.exceptions.RequestException:
                pass  # no project exists
        return existing_wikipedia_projects_language_codes


class _WikidataAPICache(EntityOntologyCache, DillCache):
    def __init__(self):
        super().__init__("wikidata")

    def get_entity_data_from_id(self, entity_id: EntityId) -> EntityData:
        return self._get_data_else_raise_exception(self.__get_entity_data_from_id_identifiers(entity_id))

    def set_entity_data_from_id(self, entity_id: EntityId, entity_data: EntityData):
        self._set_data(self.__get_entity_data_from_id_identifiers(entity_id), entity_data)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_entity_data_from_id_identifiers(self, entity_id: EntityId) -> List[str]:
        return ["entity_data", f"{entity_id}"]

    def get_event_data_from_id(self, event_id: EntityId) -> EventData:
        return self._get_data_else_raise_exception(self.__get_event_data_from_id_identifiers(event_id))

    def set_event_data_from_id(self, event_id: EntityId, event_data: EventData):
        self._set_data(self.__get_event_data_from_id_identifiers(event_id), event_data)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_event_data_from_id_identifiers(self, event_id: EntityId) -> List[str]:
        return ["event_data", f"{event_id}"]

    def is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId) -> bool:
        return self._get_data_else_raise_exception(
            self.__get_is_entity_an_instance_of_identifiers(entity_id, instance_of_entity_id)
        )

    def set_is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId, is_instance: bool):
        self._set_data(self.__get_is_entity_an_instance_of_identifiers(entity_id, instance_of_entity_id), is_instance)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_is_entity_an_instance_of_identifiers(self, entity_id: EntityId, instance_of_entity_id) -> List[str]:
        return ["is_instance_of", f"{entity_id}_{instance_of_entity_id}"]

    def get_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId) -> Set[EntityId]:
        return self._get_data_else_raise_exception(
            self.__get_all_entities_id_the_entity_is_an_instance_of_identifiers(entity_id)
        )

    def set_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId, entities: Set[EntityId]):
        self._set_data(self.__get_all_entities_id_the_entity_is_an_instance_of_identifiers(entity_id), entities)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_all_entities_id_the_entity_is_an_instance_of_identifiers(self, entity_id: EntityId) -> List[str]:
        return ["all_entities_instance", f"{entity_id}"]

    def get_official_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        return self._get_data_else_raise_exception(self.__get_official_languages_spoken_identifiers(event_id))

    def set_official_languages_spoken_where_event_happened(
        self, event_id: EntityId, official_languages: Set[ISO6391LanguageCode]
    ):
        self._set_data(self.__get_official_languages_spoken_identifiers(event_id), official_languages)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_official_languages_spoken_identifiers(self, event_id) -> List[str]:
        return ["official_spoken_languages", f"{event_id}"]

    def get_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        return self._get_data_else_raise_exception(self.__get_languages_spoken_identifiers(event_id))

    def set_languages_spoken_where_event_happened(
        self, event_id: EntityId, spoken_languages: Set[ISO6391LanguageCode]
    ):
        self._set_data(self.__get_languages_spoken_identifiers(event_id), spoken_languages)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_languages_spoken_identifiers(self, event_id) -> List[str]:
        return ["all_spoken_languages", f"{event_id}"]


class WikidataOntologyRepository(EntityOntologyRepository):
    def __init__(self):
        self.__event_ontology_api = _WikidataAPI()
        self.__event_ontology_cache = _WikidataAPICache()
        self.__entity_id_locks = defaultdict(Lock)

    def get_entity_data_from_id(self, entity_id: EntityId) -> EntityData:
        with self.__entity_id_locks[("entity_data", entity_id)]:
            try:
                entity_data = self.__event_ontology_cache.get_entity_data_from_id(entity_id)
            except NotInCacheException:
                entity_data = self.__event_ontology_api.get_entity_data_from_id(entity_id)
                self.__event_ontology_cache.set_entity_data_from_id(entity_id, entity_data)
            return entity_data

    def get_event_data_from_id(self, event_id: EntityId) -> EventData:
        with self.__entity_id_locks[("event_data", event_id)]:
            try:
                event_data = self.__event_ontology_cache.get_event_data_from_id(event_id)
            except NotInCacheException:
                event_data = self.__event_ontology_api.get_event_data_from_id(event_id)
                self.__event_ontology_cache.set_event_data_from_id(event_id, event_data)
            return event_data

    def is_entity_an_instance_of(self, entity_id: EntityId, instance_of_entity_id: EntityId) -> bool:
        with self.__entity_id_locks[("is_entity_instance_of", entity_id)]:
            try:
                is_instance = self.__event_ontology_cache.is_entity_an_instance_of(entity_id, instance_of_entity_id)
            except NotInCacheException:
                is_instance = self.__event_ontology_api.is_entity_an_instance_of(entity_id, instance_of_entity_id)
                self.__event_ontology_cache.set_is_entity_an_instance_of(entity_id, instance_of_entity_id, is_instance)
            return is_instance

    def get_all_entities_id_the_entity_is_an_instance_of(self, entity_id: EntityId) -> Set[EntityId]:
        with self.__entity_id_locks[("all_entities_instance_of", entity_id)]:
            try:
                all_entities = self.__event_ontology_cache.get_all_entities_id_the_entity_is_an_instance_of(entity_id)
            except NotInCacheException:
                all_entities = self.__event_ontology_api.get_all_entities_id_the_entity_is_an_instance_of(entity_id)
                self.__event_ontology_cache.set_all_entities_id_the_entity_is_an_instance_of(entity_id, all_entities)
            return all_entities

    def get_official_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        with self.__entity_id_locks[("official_languages", event_id)]:
            try:
                official_languages = self.__event_ontology_cache.get_official_languages_spoken_where_event_happened(
                    event_id
                )
            except NotInCacheException:
                official_languages = self.__event_ontology_api.get_official_languages_spoken_where_event_happened(
                    event_id
                )
                self.__event_ontology_cache.set_official_languages_spoken_where_event_happened(
                    event_id, official_languages
                )
            return official_languages

    def get_languages_spoken_where_event_happened(self, event_id: EntityId) -> Set[ISO6391LanguageCode]:
        with self.__entity_id_locks[("languages_spoken", event_id)]:
            try:
                spoken_languages = self.__event_ontology_cache.get_languages_spoken_where_event_happened(event_id)
            except NotInCacheException:
                spoken_languages = self.__event_ontology_api.get_languages_spoken_where_event_happened(event_id)
                self.__event_ontology_cache.set_languages_spoken_where_event_happened(event_id, spoken_languages)
            return spoken_languages
