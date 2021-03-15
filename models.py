
no_az_usage = {
    "name": "Huonompi",
    "pfizer": 1,
    "moderna": 1,
    "az": 0,
    "second_dose": 90
}

current_usage = {
    "name": "Nykyinen",
    "pfizer": 1,
    "moderna": 1,
    "az": 1,
    "second_dose": 90
}

smaller_dosage = {
    "name": "Nopeampi #1",
    "pfizer": (30.0 / 20.0),
    "moderna": 2,
    "az": 1,
    "second_dose": 180
}

third_dosage = {
    "name": "Nopeampi #2",
    "pfizer": 3,
    "moderna": 2,
    "az": 1,
    "second_dose": 180
}

shots_for_all = {
    "name": "Nopeampi #3",
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

targets = [
    {
        "target": int(facts["population"]["adult"] * 0.7),
        "name": "EU:n suosittelema 70% aikuisväestöstä"
    },
    # {
    #     "target": int(facts["population"]["all"] * 0.86),
    #     "name": "Isorokon laumasuoja"
    # },
    {
        "target": int(facts["population"]["all"] * 0.75),
        "name": "Arvio COVID-19 laumasuojasta"
    }
]
