from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from dateutil.parser import parse

no_az_usage = {
    "name": "Huonompi",
    "pfizer": 1,
    "moderna": 1,
    "az": 0,
    "second_dose": 84
}

current_usage = {
    "name": "Nykyinen",
    "pfizer": 1,
    "moderna": 1,
    "az": 1,
    "second_dose": 84
}

first_doses_first = {
    "name": "First doses first",
    "pfizer": 1,
    "moderna": 1,
    "az": 1,
    "second_dose": 180
}

# smaller_dosage = {
#     "name": "Nopeampi #1",
#     "pfizer": (30.0 / 20.0),
#     "moderna": 2,
#     "az": 1,
#     "second_dose": 180
# }

third_dosage = {
    "name": "Nopeampi #1",
    "pfizer": 3,
    "moderna": 2,
    "az": 1,
    "second_dose": 180
}

shots_for_all = {
    "name": "Nopeampi #2",
    "pfizer": 30,
    "moderna": 2,
    "az": 1,
    "second_dose": 180
}

facts = {
    # https://findikaattori.fi/fi/table/14
    "population": {
        "adult": 4475327,
        "all": 5524384,
        "children": 1049057
    }
}


@dataclass(frozen=True)
class Target:
    name: str
    value: int


targets: List[Target] = [
    Target(
        name="EU:n suosittelema 70% aikuisväestöstä",
        value=int(facts["population"]["adult"] * 0.7)
    ),
    Target(
        name="Kaikki aikuiset",
        value=facts["population"]["adult"]
    ),
    # {
    #     "target": int(facts["population"]["all"] * 0.86),
    #     "name": "Isorokon laumasuoja"
    # },
    # Target(
    #     name="COVID-19 laumasuoja (arvio)",
    #     value=int(facts["population"]["all"] * 0.75)
    # )
]


@dataclass(frozen=True)
class WeeklyDeliveryDate:
    start: datetime
    end: datetime
    rate: int


_far_future = parse("2100-04-01T00:00:00.000Z")

weekly_delivery_per_vaccine: Dict[str, List[WeeklyDeliveryDate]] = {
    "pfizer": [
        WeeklyDeliveryDate(parse("2021-03-01T00:00:00.000Z"), parse("2021-03-31T23:59:59.999Z"), 60_000),
        WeeklyDeliveryDate(parse("2021-04-01T00:00:00.000Z"), _far_future, 160_000)
    ],
    "moderna": [
        WeeklyDeliveryDate(parse("2021-03-01T00:00:00.000Z"), _far_future, 10_000),
    ],
    "az": [
        WeeklyDeliveryDate(parse("2021-03-01T00:00:00.000Z"), _far_future, 40_000),
    ],
    "j&j": [
        WeeklyDeliveryDate(parse("2021-03-01T00:00:00.000Z"), _far_future, 0),
    ],
}