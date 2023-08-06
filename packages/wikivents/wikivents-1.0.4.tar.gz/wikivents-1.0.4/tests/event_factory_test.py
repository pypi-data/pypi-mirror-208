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

from wikivents.factories import CallbackMessageHandler, LoggingCallbackMessageHandler
from wikivents.factories.wikimedia import WikimediaFactory
from wikivents.models import EntityId, ISO6391LanguageCode


class FactoriesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.san_francisco_wikidata_id = EntityId("Q62")
        self.easter_rising_wikidata_id = EntityId("Q193689")
        self.russian_revolution_wikidata_id = EntityId("Q8729")

    def test_easter_rising_labels_and_names(self):
        easter_rising = WikimediaFactory.create_event(self.easter_rising_wikidata_id)
        self.assertEqual("Easter Rising", easter_rising.label(ISO6391LanguageCode("en")))
        self.assertEqual("Insurrection de Pâques 1916", easter_rising.label(ISO6391LanguageCode("fr")))
        self.assertEqual(
            "an armed insurrection in Ireland during Easter Week, 1916",
            easter_rising.description(ISO6391LanguageCode("en")),
        )
        self.assertEqual(
            "Ribellione avvenuta in Irlanda durante la settimana di Pasqua del 1916",
            easter_rising.description(ISO6391LanguageCode("it")),
        )

    def test_easter_rising_places(self):
        easter_rising = WikimediaFactory.create_event(self.easter_rising_wikidata_id)
        places_labels = {place_label.id for place_label in easter_rising.places()}
        united_kingdom_of_great_britain_and_ireland, dublin = EntityId("Q174193"), EntityId("Q1761")
        self.assertIn(united_kingdom_of_great_britain_and_ireland, places_labels)
        self.assertIn(dublin, places_labels)

    def test_easter_rising_participants(self):
        easter_rising = WikimediaFactory.create_event(self.easter_rising_wikidata_id)
        self.assertIsInstance(easter_rising.participants(), set)
        self.assertIsInstance(easter_rising.gpe, list)
        self.assertIsInstance(easter_rising.per, list)
        self.assertIsInstance(easter_rising.org, list)

    def test_easter_rising_processed_languages(self):
        easter_rising = WikimediaFactory.create_event(self.easter_rising_wikidata_id)
        self.assertEqual({"es", "it", "en", "fr", "de"}, easter_rising.processed_languages_iso_639_1_codes)

    def test_easter_rising_dates(self):
        easter_rising = WikimediaFactory.create_event(self.easter_rising_wikidata_id)
        self.assertEqual("1916-04-24T00:00:00+00:00", easter_rising.beginning.isoformat())
        self.assertEqual("1916-04-30T00:00:00+00:00", easter_rising.end.isoformat())

    def test_russian_revolution_labels_and_names(self):
        russian_revolution = WikimediaFactory.create_event(self.russian_revolution_wikidata_id)
        self.assertEqual("Russian Revolution", russian_revolution.label(ISO6391LanguageCode("en")))
        self.assertEqual("Revolución rusa", russian_revolution.label(ISO6391LanguageCode("es")))
        self.assertEqual(
            "20th-century revolution leading to the downfall of the Russian monarchy",
            russian_revolution.description(ISO6391LanguageCode("en")),
        )
        self.assertEqual(
            "révolution du XXe siècle marquant l'arrivée au pouvoir des communistes",
            russian_revolution.description(ISO6391LanguageCode("fr")),
        )

    def test_russian_revolution_places(self):
        russian_revolution = WikimediaFactory.create_event(self.russian_revolution_wikidata_id)
        places_labels = {place_label.id for place_label in russian_revolution.places()}
        russian_empire = EntityId("Q34266")
        self.assertIn(russian_empire, places_labels)

    def test_russian_revolution_participants(self):
        russian_revolution = WikimediaFactory.create_event(self.russian_revolution_wikidata_id)
        self.assertIsInstance(russian_revolution.participants(), set)
        self.assertIsInstance(russian_revolution.gpe, list)
        self.assertIsInstance(russian_revolution.per, list)
        self.assertIsInstance(russian_revolution.org, list)

    def test_russian_revolution_processed_languages(self):
        russian_revolution = WikimediaFactory.create_event(self.russian_revolution_wikidata_id)
        self.assertEqual(
            {"es", "it", "en", "fr", "de", "ru", "fi", "pl", "sv"},
            russian_revolution.processed_languages_iso_639_1_codes,
        )

    def test_russian_revolution_dates(self):
        russian_revolution = WikimediaFactory.create_event(self.russian_revolution_wikidata_id)
        self.assertEqual("1917-01-01T00:00:00+00:00", russian_revolution.beginning.isoformat())
        with self.assertRaises(ValueError):
            russian_revolution.end

    def test_callback_is_called_when_processing_event(self):
        def callback(msg, step, nb):
            self.count += 1

        self.count = 0
        WikimediaFactory.create_event(EntityId("Q193689"), CallbackMessageHandler(callback))
        self.assertEqual(self.count, 9)

    def test_callback_and_logging_is_called_when_processing_event(self):
        def callback(msg, step, nb):
            self.count += 1

        self.count = 0
        WikimediaFactory.create_event(EntityId("Q193689"), LoggingCallbackMessageHandler(callback))
        self.assertEqual(self.count, 9)


if __name__ == "__main__":
    unittest.main()
