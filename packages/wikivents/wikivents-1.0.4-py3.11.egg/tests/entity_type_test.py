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

from wikivents.models import EntityType, EntityId


class TestEntityType(unittest.TestCase):
    def setUp(self) -> None:
        self.human_wikidata_id = EntityId("Q5")
        self.organisation_wikidata_id = EntityId("Q43229")
        self.position_wikidata_id = EntityId("Q4164871")
        self.locality_wikidata_id = EntityId("Q3257686")
        self.country_wikidata_id = EntityId("Q6256")
        self.territorial_entity_wikidata_id = EntityId("Q56061")
        self.occurrence_wikidata_id = EntityId("Q1190554")
        self.event_wikidata_id = EntityId("Q1656682")

    def tearDown(self) -> None:
        pass

    def test_entity_type_Q5_human_is_a_person(self):
        self.assertIn(EntityType.PERSON, EntityType.get_types({self.human_wikidata_id}))

    def test_entity_type_Q43229_organisation_is_a_org(self):
        self.assertIn(EntityType.ORG, EntityType.get_types({self.organisation_wikidata_id}))

    def test_entity_type_Q4164871_position_is_a_org(self):
        self.assertIn(EntityType.ORG, EntityType.get_types({self.position_wikidata_id}))

    def test_entity_type_Q3257686_locality_is_a_gpe(self):
        self.assertIn(EntityType.GPE, EntityType.get_types({self.locality_wikidata_id}))

    def test_entity_type_Q6256_country_is_a_gpe(self):
        self.assertIn(EntityType.GPE, EntityType.get_types({self.country_wikidata_id}))

    def test_entity_type_Q56061_territorial_entity_is_a_gpe(self):
        self.assertIn(EntityType.GPE, EntityType.get_types({self.territorial_entity_wikidata_id}))

    def test_entity_type_Q1190554_occurrence_is_an_event(self):
        self.assertIn(EntityType.EVENT, EntityType.get_types({self.occurrence_wikidata_id}))

    def test_entity_type_Q56061_event_is_an_event(self):
        self.assertIn(EntityType.EVENT, EntityType.get_types({self.event_wikidata_id}))


if __name__ == "__main__":
    unittest.main()
