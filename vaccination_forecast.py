from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dateutil.parser import parse

from fetch_data import VaccinationRecord, fetch_vaccination_data


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


def dosage_for_day(day: datetime) -> Dict[str, int]:
    dosage = {
        "pfizer": 0,
        "moderna": 0,
        "az": 0
    }
    k: str
    v: List[WeeklyDeliveryDate]
    wd: WeeklyDeliveryDate
    for k, v in weekly_delivery_per_vaccine.items():
        for wd in v:
            if wd.start <= day < wd.end:
                # Assume vaccine is delivered continuously over week
                dosage[k] = wd.rate / 7
    return dosage


def total_shots_for_day(day: datetime, pfizer_multiplier: int, moderna_multiplier: int, az_multiplier: int) -> int:
    dosage: Dict[str, int] = dosage_for_day(day)
    total = 0
    for k, v in dosage.items():
        if k == "pfizer":
            total += pfizer_multiplier * v
        elif k == "moderna":
            total += moderna_multiplier * v
        elif k == "az":
            total += az_multiplier * v
        else:
            total += 1
    return int(total)


def forecast(days_to_forecast: int,
             total_population: int,
             vaccinated: List[VaccinationRecord],
             second_shot_portion=0.0,
             second_dosage_interval=90,
             pfizer_multiplier=1,
             moderna_multiplier=1,
             az_multiplier=1) -> List[VaccinationRecord]:
    """
    Potentially incorrect assumptions and their effects:
    Vaccinations are uniformly distributed over all seven days of the week (too optimistic)
    We ignore the 1.8% or so of the population that already has two shots by assuming that no one has (too pessimistic)
    We assume that everyone has had their shot just before forecasting starts so their second shot is long away (too optimistic)
    We ignore one-shot vaccines like Johnson&Johnson for now (too pessimistic)
    We ignore vaccines that we know nothing of delivery (too pessimistic)
    :param total_population: How many people we can vaccinate at most
    :param second_shot_portion: At most what portion of shots will be given to second shot
    :param days_to_forecast: How many days we forecast?
    :param vaccinated: history information on vaccinations
    :param second_dosage_interval: How long a person wait before consuming another shot
    :param pfizer_multiplier: How many people will we vaccinate with one shot of Pfizer/BioNTech vaccine?
    :param moderna_multiplier: How many people will we vaccinate with one shot of Moderna vaccine?
    :param az_multiplier: How many people will we vaccinate with one shot of Astra-Zeneca vaccine?
    :return:
    """
    data: List[VaccinationRecord] = sorted(vaccinated, key=lambda x: x.date)
    last_date = data[-1].date
    first_shot_only = [x.amount for x in vaccinated]
    sum_vaccinated = data[-1].amount
    forecast_data: List[VaccinationRecord] = []

    for x in range(1, days_to_forecast + 1, 1):
        today = last_date + timedelta(days=x)
        first_shot_index = x - second_dosage_interval
        needs_second_shot = 0 if first_shot_index < 0 else first_shot_only[first_shot_index]
        shots_for_today = total_shots_for_day(today,
                                              pfizer_multiplier=pfizer_multiplier,
                                              moderna_multiplier=moderna_multiplier,
                                              az_multiplier=az_multiplier)
        # Need to transform first_shot_only into other form.
        second_shots_delivered = min(int(second_shot_portion * shots_for_today), needs_second_shot)
        first_shots_delivered = shots_for_today - second_shots_delivered
        sum_vaccinated += first_shots_delivered
        if sum_vaccinated > total_population:
            first_shots_delivered -= sum_vaccinated - total_population
            second_shots_delivered = min(needs_second_shot, shots_for_today - first_shots_delivered)
            sum_vaccinated = total_population
        first_shot_only.append(first_shots_delivered)
        forecast_data.append(VaccinationRecord(today, float(sum_vaccinated)))

    return forecast_data


def main():
    data = fetch_vaccination_data()
    forecasts = forecast(180, 5524384, data)
    print(forecasts)


if __name__ == "__main__":
    main()
