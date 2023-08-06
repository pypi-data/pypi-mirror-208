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
import re
from collections import defaultdict
from threading import Lock
from typing import Set, Dict, List

import mwclient
import requests
from mwclient.page import Page

from wikivents.cache import DillCache
from wikivents.exc import NotInCacheException
from wikivents.models import ParticipatingEntity, EntityId, ISO6391LanguageCode, Entity, EntityCountByLanguage
from wikivents.ontology import EntityOntologyRepository
from wikivents.resource import Resource, EntityResourceAPI, EntityResourceRepository, EntityResourceCache
from wikivents.resource.exc import ResourceInLanguageDoesNotExist, ResourceDoesNotExist


class WikipediaArticle(Resource):
    def __init__(self, wikipedia_page: Page):
        self._wikipedia_page = wikipedia_page
        self._article_name = wikipedia_page.page_title
        self._iso_639_1_language_code = wikipedia_page.pagelanguage

    def content(self) -> str:
        return self._wikipedia_page.text()

    def entities(self) -> Dict[str, int]:
        entity_ids_count = defaultdict(int)
        entities_internal_links = self.__get_internal_links()
        for entity_wikipedia_link_name in entities_internal_links:
            entity_ids_count[entity_wikipedia_link_name] = entities_internal_links.count(entity_wikipedia_link_name)
        return entity_ids_count

    def iso_639_1_language(self) -> ISO6391LanguageCode:
        return self._iso_639_1_language_code

    def __get_internal_links(self) -> List[str]:
        """
        :return: the named entities found in the page lead section (i.e: {"Nicolas II"})
        """
        found_entities_internal_links = list()
        # On Wikipedia, internal links are represented as ’[[INTERNAL_LINK_NAME|TEXT_TO_PRINT]]’.
        entities_found_in_the_article_section = re.findall(r"\[\[(.*?)\]\]", self.content(), re.DOTALL)
        for wikipedia_entity in entities_found_in_the_article_section:
            wikipedia_entity_internal_link = wikipedia_entity.split("|")[0]
            found_entities_internal_links.append(wikipedia_entity_internal_link)
        return found_entities_internal_links

    def __len__(self):
        return len(self._wikipedia_page.text())

    def __str__(self):
        return f"WikipediaArticle({self._wikipedia_page.page_title}, {self._wikipedia_page.pagelanguage})"


class WikipediaArticleLeadSection(WikipediaArticle):
    __MEDIA_WIKI_API_INDEX_FOR_INTRODUCTION_SECTION = 0

    def __init__(self, wikipedia_page: Page):
        WikipediaArticle.__init__(self, wikipedia_page)

    def content(self) -> str:
        return self._wikipedia_page.text(section=self.__MEDIA_WIKI_API_INDEX_FOR_INTRODUCTION_SECTION)

    def __len__(self):
        return len(self._wikipedia_page.text(section=self.__MEDIA_WIKI_API_INDEX_FOR_INTRODUCTION_SECTION))

    def __str__(self):
        return f"WikipediaArticleLeadSection({self._wikipedia_page.page_title}, {self._wikipedia_page.pagelanguage})"


class _WikipediaResourceCache(EntityResourceCache, DillCache):
    def __init__(self, iso_639_1_language_code: str, wikidata_ontology_repository: EntityOntologyRepository):
        super().__init__("wikipedia")
        self.__entity_ontology_repository = wikidata_ontology_repository
        self.__iso_639_1_language_code = iso_639_1_language_code

    def get_resource_from_label(self, label: str) -> Resource:
        return self._get_data_else_raise_exception(self.__get_resource_from_label_identifiers(label))

    def set_resource_from_label(self, label: str, resource: Resource):
        self._set_data(self.__get_resource_from_label_identifiers(label), resource)

    def __get_resource_from_label_identifiers(self, label: str) -> List[str]:
        return ["resource", f"wikipedia_{self.__iso_639_1_language_code}_{label}"]

    def get_participating_entities_count_by_language(self, resource: Resource) -> Set[ParticipatingEntity]:
        return self._get_data_else_raise_exception(self.__get_participating_entities_identifiers(resource))

    def set_participating_entities(self, resource: Resource, participating_entities: Set[ParticipatingEntity]):
        self._set_data(self.__get_participating_entities_identifiers(resource), participating_entities)

    def __get_participating_entities_identifiers(self, resource: Resource) -> List[str]:
        return ["participating_entities", f"{self.__iso_639_1_language_code}_{resource}"]


class _WikipediaResourceAPI(EntityResourceAPI):
    def __init__(self, iso_639_1_language_code: str, wikidata_ontology_repository: EntityOntologyRepository):
        self.__entity_ontology_repository = wikidata_ontology_repository
        self.__iso_639_1_language_code = iso_639_1_language_code
        try:
            self._site = mwclient.Site(f"{self.__iso_639_1_language_code}.wikipedia.org")
        except (mwclient.InvalidResponse, requests.exceptions.ConnectionError) as connection_error:
            raise ResourceInLanguageDoesNotExist(
                f"There is no existing Wikipedia project in language ’{iso_639_1_language_code}’"
                f" ({connection_error})."
            )
        except requests.exceptions.HTTPError as http_error:
            raise ResourceInLanguageDoesNotExist(
                f"Connection to the Wikipedia project in language ’{iso_639_1_language_code}’"
                f"failed due to an HTTP Error ({http_error})."
            )

    def get_resource_from_label(self, label: str) -> Resource:
        try:
            resource = WikipediaArticleLeadSection(self._site.pages[label])
        except KeyError:
            raise ResourceDoesNotExist(
                f"No resource found for entity ‘{label}’ in language ‘{self.__iso_639_1_language_code}’"
            )
        return resource

    def get_participating_entities_count_by_language(self, resource: Resource) -> Set[EntityCountByLanguage]:
        participating_entities = dict()
        for entity_name, entity_count in resource.entities().items():
            if entity_name not in participating_entities:
                try:
                    entity_id = self.__get_entity_id_from_label(entity_name)
                except ValueError:
                    #  No page exist for the label on this site
                    pass
                else:
                    entity_data = self.__entity_ontology_repository.get_entity_data_from_id(entity_id)
                    entity = Entity(entity_data)
                    participating_entities[entity_name] = EntityCountByLanguage(
                        entity,
                        entity_count,
                        resource.iso_639_1_language(),
                    )
        return set(participating_entities.values())

    def __get_entity_id_from_label(self, label: str) -> EntityId:
        """
        :raises ValueError: when no page exists for the given label or nothing is returned by the API.

        .. seealso:: https://en.wikipedia.org/wiki/Wikipedia:Finding_a_Wikidata_ID

        For example, the query below:
        https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles=Kofoworola_Abeni_Pratt&format=json
        returns the following JSON document:

        .. code-block:: text

            {
                "batchcomplete": "",
                "query": {
                "normalized": […],
                "pages": {
                    "51046741": {
                        "pageid": 51046741,
                        "ns": 0,
                        "title": "Kofoworola Abeni Pratt",
                        "pageprops": {
                            "defaultsort": "Pratt, Kofoworola Abeni",
                            "wikibase-shortdesc": "20th-century Nigerian-born nurse; […] of Nigeria",
                            "wikibase_item": "Q25796287"
                        }
                    }
                }
            }

        """
        response = self._site.get(
            action="query",
            format="json",
            titles=label,
            prop="pageprops",  # query “page properties”
            redirects="",  # redirects is the page has move or has been rewritten
        )
        wikipedia_pages_response = response.get("query").get("pages")

        if not wikipedia_pages_response or not self.__wikipedia_page_response_has_pages_properties(
            wikipedia_pages_response
        ):
            raise ValueError(f"No page exist for {label} on ’{self._site.host}’")

        entity_id = EntityId(
            self.__get_wikidata_pages_response_linked_wikidata_entity(wikipedia_pages_response)
            .get("pageprops")
            .get("wikibase_item")
        )

        if entity_id is None:
            raise ValueError(f"No entity identifier found for entity with label {label}.")

        return entity_id

    def __wikipedia_page_response_has_pages_properties(self, wikipedia_pages_response: Dict[EntityId, Dict]):
        return "pageprops" in self.__get_wikidata_pages_response_linked_wikidata_entity(wikipedia_pages_response)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def __get_wikidata_pages_response_linked_wikidata_entity(self, wikipedia_pages_response: Dict[EntityId, Dict]):
        return next(iter(wikipedia_pages_response.values()))


class WikipediaResourceRepository(EntityResourceRepository):
    def __init__(self, iso_639_1_language_code: str, wikidata_ontology_repository: EntityOntologyRepository):
        self.__entity_resource_api = _WikipediaResourceAPI(iso_639_1_language_code, wikidata_ontology_repository)
        self.__entity_resource_cache = _WikipediaResourceCache(iso_639_1_language_code, wikidata_ontology_repository)
        self.__resource_locks = defaultdict(Lock)

    def get_resource_from_label(self, label: str) -> Resource:
        with self.__resource_locks[("resource_from_label", label)]:
            try:
                resource = self.__entity_resource_cache.get_resource_from_label(label)
            except NotInCacheException:
                resource = self.__entity_resource_api.get_resource_from_label(label)
                self.__entity_resource_cache.set_resource_from_label(label, resource)
            return resource

    def get_participating_entities_count_by_language(self, resource: Resource) -> Set[ParticipatingEntity]:
        with self.__resource_locks["participating_entities", resource.content()[:50]]:
            try:
                participating_entities = self.__entity_resource_cache.get_participating_entities_count_by_language(
                    resource
                )
            except NotInCacheException:
                participating_entities = self.__entity_resource_api.get_participating_entities_count_by_language(
                    resource
                )
                self.__entity_resource_cache.set_participating_entities(resource, participating_entities)
            return participating_entities
