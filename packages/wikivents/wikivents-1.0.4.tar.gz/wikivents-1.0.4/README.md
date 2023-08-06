# `wikivents`

This Python package is used to represent events based on both ontologies and semi-structured databases. Up to now, only Wikidata and Wikipedia are implemented and provide these data. The name of this package, `wikivents` show this legacy.

### Events

An event is an ontology entity. For Wikidata, an event is an instance of an [occurrence (Q1190554)](https://www.wikidata.org/wiki/Q1190554) or of an [event (Q1656682)](https://www.wikidata.org/wiki/Q1656682).

A **event** is defined by few characteristics:
 * **A type**: on Wikidata, this defines the type of the event. For instance, [rebellion (Q124734)](https://www.wikidata.org/wiki/Q124734) on Wikidata. This information is provided by the `wd:P31` or `rdf:type`, depending on the source.
 * **Date** of occurrence, converted if necessary in the Gregorian calendar.
 * **Location where the event happened**.
 * The entities related to the event. The extraction process is based on semi-strucuted databases, which are processed in search of entities (people involved, places, etc). Entities are counted. This index shows the relevance of the entity in relation to the event. We assume the entities found in multiple lead sections are important entities in the event description.

## Usage

The process of gathering data from multiple APIs (ontologies and semi-structured databases) can take a long time. We implemented a cache which speeds up queries and prevents from querying twice the same data.

Up to now, the only implemented toolchain is based on Wikimedia foundation projects: Wikidata for the ontology and Wikipedia articles for semi-structured databases. Then it is possible to get the representation of an event using the `WikimediaFactory` object, as in the example below:

```python
from wikivents.factories.wikimedia import WikimediaFactory
from wikivents.models import EntityId

easter_rising_entity_id = EntityId("Q193689")
easter_rising_event = WikimediaFactory.create_event(easter_rising_entity_id)
```

The previous code takes the [Easter Rising event](https://en.wikipedia.org/wiki/Easter_Rising) entity id (`Q193689`)' as input. If using another `Factory` which processes other ontologies, the entry point will obviously not be the same.

From the `easter_rising_event` object, it is possible to access multiple attributes:

* The **event identifier**, which comes from the ontology itself:
```python
easter_rising_event.id
Out[5]: 'Q193689'
```

* The **event label**, in any possible language. If unavailable, will return an empty string.
```python
easter_rising_event.label("fr")
Out[7]: 'Insurrection de Pâques 1916'
```

* The **event alternative names**, which means all the names that are used in a specific language to speak about the event.
```python
easter_rising_event.names("de")
Out[8]: {'Easter Rising', 'Irischer Osteraufstand 1916', 'Osteraufstand'}
```

* The **event description**, in plain text.
```python
easter_rising_event.description("en")
Out[9]: 'an armed insurrection in Ireland during Easter Week, 1916'
```

* The **event boundary dates**, beginning and end.
```python
easter_rising_event.beginning, easter_rising_event.end
Out[12]: (datetime.datetime(1916, 4, 24, 0, 0, tzinfo=datetime.timezone.utc),  datetime.datetime(1916, 4, 30, 0, 0, tzinfo=datetime.timezone.utc))
```

* The entities involved, accessible using the `gpe` property for **GPE**, `org` property for **ORG** and `per` property for **PER** entities.
```python
easter_rising_event.gpe
Out[13]: [ParticipatingEntity(entity=<Entity(Q1761, Dublin)>, count=8),ParticipatingEntity(entity=<Entity(Q27, Ireland)>, count=5)]
```

## Encode events in reusable formats

The `wikivents` library also provides encoders which are used to transform the event object into other formats, easier to manipulate. From now on, we provide a `DictEncoder` which make it easy to create a JSON file from it.

```python
from wikivents.model_encoders import EventToDictEncoder
from wikivents.models import ISO6391LanguageCode

encoder = EventToDictEncoder(easter_rising_event, ISO6391LanguageCode("en"))
encoder.encode()
```

The purpose of encoders is to provide all the possible knowledge acquired about events and to show involved entities. It is also possible to add a parameter to the `encode()` method, `participating_entities_ratio_to_keep` to indicate which entities will be kept. It is a value comprised between 0 and 1. `1` means to keep all the participating entities, `0.5` to keep them only if they were found in at least 50% of the total number of processed semi-structured databases.

Below is an example, and the associated JSON output:

```python
import json

with open("easter_rising_event.json", mode="w") as easter_rising_json_file:
    json.dump(encoder.encode(), easter_rising_json_file)
```

```json
[
  {
    "Q193689": {
      "iso_639_1_language_code": "en",
      "id": "Q193689",
      "type": "EVENT",
      "label": "Easter Rising",
      "description": "an armed insurrection in Ireland during Easter Week, 1916",
      "names": [
        "1916 Rising",
        "Easter Rebellion",
        "Easter Rising"
      ],
      "processed_languages": [
        "de",
        "it",
        "es",
        "fr",
        "en"
      ],
      "entities_kept_if_mentioned_in_more_at_least_X_languages": 2.5,
      "start": "1916-04-24T00:00:00+00:00",
      "end": "1916-04-30T00:00:00+00:00",
      "entities": {
        "per": [
          {
            "id": "Q213374",
            "type": [
              "PERSON"
            ],
            "label": "James Connolly",
            "description": "James Connolly",
            "names": [
              "James Connolly"
            ],
            "count": 3
          },
          {
            "id": "Q274143",
            "type": [
              "PERSON"
            ],
            "label": "Patrick Pearse",
            "description": "Patrick Pearse",
            "names": [
              "Patrick Henry Pearse",
              "Patrick Pearse",
              "Padraig Pearse"
            ],
            "count": 3
          }
        ],
        "gpe": [
          {
            "id": "Q1761",
            "type": [
              "GPE"
            ],
            "label": "Dublin",
            "description": "Dublin",
            "names": [
              "City of Dublin",
              "Baile Átha Cliath",
              "Dublin",
              "Dublin city"
            ],
            "count": 8
          },
          {
            "id": "Q27",
            "type": [
              "GPE",
              "ORG"
            ],
            "label": "Ireland",
            "description": "Ireland",
            "names": [
              "🇮🇪",
              "Eire",
              "Éire",
              "Ireland",
              "ie",
              "ireland",
              "IRL",
              "Ireland, Republic of",
              "Republic of Ireland",
              "Hibernia",
              "IE",
              "Southern Ireland"
            ],
            "count": 5
          },
          {
            "id": "Q145",
            "type": [
              "GPE",
              "ORG"
            ],
            "label": "United Kingdom",
            "description": "United Kingdom",
            "names": [
              "G.B.",
              "GBR",
              "United Kingdom",
              "U. K.",
              "U K",
              "GB",
              "UK",
              "United Kingdom of Great Britain and Northern Ireland",
              "G B R",
              "Marea Britanie",
              "G. B. R.",
              "G B",
              "G. B.",
              "G.B.R.",
              "🇬🇧",
              "U.K.",
              "Great Britain"
            ],
            "count": 3
          }
        ],
        "org": [
          {
            "id": "Q27",
            "type": [
              "GPE",
              "ORG"
            ],
            "label": "Ireland",
            "description": "Ireland",
            "names": [
              "🇮🇪",
              "Eire",
              "Éire",
              "Ireland",
              "ie",
              "ireland",
              "IRL",
              "Ireland, Republic of",
              "Republic of Ireland",
              "Hibernia",
              "IE",
              "Southern Ireland"
            ],
            "count": 5
          },
          {
            "id": "Q1074958",
            "type": [
              "ORG"
            ],
            "label": "Irish Volunteers",
            "description": "Irish Volunteers",
            "names": [
              "Irish Volunteers",
              "Irish Volunteer Army",
              "Irish Volunteer Force"
            ],
            "count": 3
          },
          {
            "id": "Q145",
            "type": [
              "GPE",
              "ORG"
            ],
            "label": "United Kingdom",
            "description": "United Kingdom",
            "names": [
              "G.B.",
              "GBR",
              "United Kingdom",
              "U. K.",
              "U K",
              "GB",
              "UK",
              "United Kingdom of Great Britain and Northern Ireland",
              "G B R",
              "Marea Britanie",
              "G. B. R.",
              "G B",
              "G. B.",
              "G.B.R.",
              "🇬🇧",
              "U.K.",
              "Great Britain"
            ],
            "count": 3
          },
          {
            "id": "Q222595",
            "type": [
              "ORG"
            ],
            "label": "British Army",
            "description": "British Army",
            "names": [
              "British Army",
              "army of the United Kingdom"
            ],
            "count": 3
          },
          {
            "id": "Q1190570",
            "type": [
              "ORG"
            ],
            "label": "Irish Citizen Army",
            "description": "Irish Citizen Army",
            "names": [
              "Irish Citizen Army"
            ],
            "count": 3
          },
          {
            "id": "Q427496",
            "type": [
              "ORG"
            ],
            "label": "Cumann na mBan",
            "description": "Cumann na mBan",
            "names": [
              "Cumann na mBan",
              "CnamB",
              "The Irishwomen's Council"
            ],
            "count": 3
          }
        ]
      }
    }
  }
]
```
