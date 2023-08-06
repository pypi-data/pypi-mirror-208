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
import unittest

from wikivents.factories.wikimedia import WikimediaFactory
from wikivents.models import EntityId, EntityType, ISO6391LanguageCode
from wikivents.ontology.wikidata import WikidataOntologyRepository


class EntityFactoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.san_francisco_wikidata_id = EntityId("Q62")
        self.easter_rising_wikidata_id = EntityId("Q193689")

    def test_san_francisco_entity_labels_and_names(self):
        san_francisco_entity = WikimediaFactory.create_entity(self.san_francisco_wikidata_id)
        self.assertEqual("San Francisco", san_francisco_entity.label(ISO6391LanguageCode("en")))
        self.assertIsInstance(san_francisco_entity.names(ISO6391LanguageCode("en")), set)
        self.assertEqual(
            "consolidated city-county in California, United States",
            san_francisco_entity.description(ISO6391LanguageCode("en")),
        )

    def test_san_francisco_entity_type_is_gpe(self):
        san_francisco_entity = WikimediaFactory.create_entity(self.san_francisco_wikidata_id)
        self.assertIn(EntityType.GPE, san_francisco_entity.types())

    def test_easter_rising_types_contain_rebellion_and_occurrence(self):
        easter_rising_data = WikidataOntologyRepository().get_entity_data_from_id(self.easter_rising_wikidata_id)
        rebellion_entity_id, occurrence_entity_id = EntityId("Q124734"), EntityId("Q1190554")
        self.assertIn(rebellion_entity_id, easter_rising_data.hierarchical_instance_of_ids)
        self.assertIn(occurrence_entity_id, easter_rising_data.hierarchical_instance_of_ids)

    def test_easter_rising_entity_type_is_an_event(self):
        easter_rising_entity = WikimediaFactory.create_entity(self.easter_rising_wikidata_id)
        self.assertIn(EntityType.EVENT, easter_rising_entity.types())

    def test_easter_rising_instance_of_data_is_rebellion(self):
        easter_rising_entity = WikimediaFactory.create_entity(self.easter_rising_wikidata_id)
        self.assertEqual(1, len(easter_rising_entity.types_as_entities()))

        rebellion_wikidata_id = EntityId("Q124734")
        self.assertEqual(rebellion_wikidata_id, list(easter_rising_entity.types_as_entities())[0].id)


if __name__ == "__main__":
    unittest.main()
