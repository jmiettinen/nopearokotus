from datetime import datetime
from typing import Dict, List, Union, Tuple, Optional

from models import Target


def fetch_data_for_main(forecast_length: int = 270) -> Tuple[Dict[str, List[float]], List[datetime], List[Target]]:
    from fetch_data import fetch_vaccination_data
    from models import current_usage, shots_for_all, third_dosage, targets, facts, no_az_usage
    from vaccination_forecast import forecast

    data = fetch_vaccination_data()
    parameters = [
        shots_for_all,
        third_dosage,
        current_usage,
        no_az_usage,
    ]
    timeseries: Dict[str, List[float]] = {}
    dates: List[datetime] = []
    for param in parameters:
        forecasted_data = forecast(forecast_length, facts["population"]["all"], data,
                                   second_shot_interval=param["second_dose"],
                                   second_shot_portion=0.5,
                                   pfizer_multiplier=param["pfizer"], moderna_multiplier=param["moderna"],
                                   az_multiplier=param["az"])
        timeseries[param["name"]] = [float(x.amount) for x in forecasted_data]
        dates = [x.date for x in forecasted_data]
    return timeseries, dates, targets


def find_target_date(vaccinated: List[float], target: int, dates: List[datetime]) -> Optional[datetime]:
    for i in range(len(vaccinated)):
        if vaccinated[i] >= target:
            return dates[i]
    return None


def main():
    timeseries, dates, targets = fetch_data_for_main(400)

    target: Target
    print("Rokotustapa      Ero Tavoite saavutettu")
    for target in targets:
        print()
        print(target.name)
        dates_for_target = [(k, find_target_date(v, target.value, dates)) for k, v in timeseries.items()]
        baseline_date = [x for x in dates_for_target if x[0] == "Nykyinen"][0][1]
        for name_and_date in dates_for_target:
            diff_to_baseline = (name_and_date[1] - baseline_date).days
            date_as_string = name_and_date[1].strftime("%Y-%m-%d")
            formatted = "{:15} {:4} {}".format(name_and_date[0], diff_to_baseline, date_as_string)
            print(formatted)


if __name__ == "__main__":
    main()
