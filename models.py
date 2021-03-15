
current_usage = {
    "name": "P1_M1_90",
    "pfizer": 1,
    "moderna": 1,
    "az": 1,
    "second_dose": 90
}

smaller_dosage = {
    "name": "P1.5_M2_90",
    "pfizer": (30.0 / 20.0),
    "moderna": 2,
    "az": 1
    "second_dose": 90
}

third_dosage = {
    "name": "P3_M2_90",
    "pfizer": 3,
    "moderna": 2,
    "az": 1,
    "second_dose": 90
}

shots_for_all = {
    "name": "P30_M2_180",
    "pfizer": 30,
    "moderna": 2,
    "az": 1
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
    {
        "target": int(facts["population"]["all"] * 0.86),
        "name": "Isorokon laumasuoja"
    },
    {
        "target": int(facts["population"]["all"] * 0.75),
        "name": "Arvio COVID-19 laumasuojasta"
    }
]
