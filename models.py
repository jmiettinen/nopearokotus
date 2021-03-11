
current_usage = {
    "name": "P1_M1_90",
    "pfizer": 1,
    "moderna": 1,
    "second_dose": 90
}

half_dosage = {
    "name": "P2_M2_90",
    "pfizer": 2,
    "moderna": 2,
    "second_dose": 90
}

third_dosage = {
    "name": "P3_M2_90",
    "pfizer": 3,
    "moderna": 2,
    "second_dose": 90
}

shots_for_all = {
    "name": "P30_M2_180",
    "pfizer": 30,
    "moderna": 2,
    "second_dose": 180
}

facts = {
    "population": {
        "adult": 4475327,
        "all": 5524384,
        "children": 1049057
    },
    "targets": {
        "eu": {},
        "herd immunity": {}
    }
}

facts["targets"]["eu"] = int(facts["population"]["adult"] * 0.7)
facts["targets"]["herd immunity"] = {
    "smallpox": int(facts["population"]["all"] * 0.86),
    "covid": int(facts["population"]["all"] * 0.75)
}

