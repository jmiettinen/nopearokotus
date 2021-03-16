from dataclasses import dataclass
from datetime import datetime
from typing import List
from dateutil.parser import parse

import requests

VACCINATION_URL = "https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishVaccinationData"


@dataclass(frozen=True)
class VaccinationRecord:
    date: datetime
    amount: int


def fetch_vaccination_data() -> List[VaccinationRecord]:
    res = requests.get(VACCINATION_URL)
    return [VaccinationRecord(parse(x["date"]), x["shots"]) for x in res.json() if x["area"] == "Finland"]


if __name__ == "__main__":
    print(fetch_vaccination_data())
