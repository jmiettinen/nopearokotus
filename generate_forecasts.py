from datetime import datetime
from typing import Dict, List, Tuple, Optional

from models import Target, first_doses_first


def fetch_data_for_main(forecast_length: int = 270) -> Tuple[Dict[str, List[float]], List[datetime], List[Target]]:
    from fetch_data import fetch_vaccination_data
    from models import current_usage, shots_for_all, third_dosage, targets, facts, no_az_usage
    from vaccination_forecast import forecast

    data = fetch_vaccination_data()
    parameters = [
        shots_for_all,
        third_dosage,
        first_doses_first,
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


def print_summary(timeseries: Dict[str, List[float]], dates: List[datetime],targets:  List[Target]) -> None:
    target: Target
    print("Rokotustapa           Ero Tavoite saavutettu")
    for target in targets:
        print()
        print(target.name)
        dates_for_target = [(k, find_target_date(v, target.value, dates)) for k, v in timeseries.items()]
        baseline_date = [x for x in dates_for_target if x[0] == "Nykyinen"][0][1]
        for name_and_date in dates_for_target:
            diff_to_baseline = (name_and_date[1] - baseline_date).days
            date_as_string = name_and_date[1].strftime("%Y-%m-%d")
            formatted = "{:20} {:4} {}".format(name_and_date[0], diff_to_baseline, date_as_string)
            print(formatted)


def week_of(date: datetime) -> int:
    return date.isocalendar()[1]


def as_diff_list(data: List[float]) -> List[float]:
    diff_list = [0]
    for i in range(1, len(data)):
        diff_list.append(data[i] - data[i-1])
    return diff_list


def print_detail(timeseries: Dict[str, List[float]], dates: List[datetime]) -> None:
    start_index = 0
    end_index = 0

    diff_lists = [as_diff_list(x) for x in timeseries.values()]

    print("Week " + " ".join(["{:18}".format(k) for k in timeseries.keys()]))
    while end_index <= len(dates):
        if end_index == len(dates) or (week_of(dates[start_index]) != week_of(dates[end_index])):
            week_number = week_of(dates[start_index])
            values = [sum(x[start_index:end_index]) for x in diff_lists]
            formatted = "{:4} ".format(week_number) + " ".join(["{:15}".format(x) for x in values])
            print(formatted)
            start_index = end_index
            if end_index == len(dates):
                break
        else:
            end_index += 1
    print("Sum " + " ".join(["{:18}".format(sum(k)) for k in diff_lists]))


def main():
    timeseries, dates, targets = fetch_data_for_main(400)
    import argparse
    parser = argparse.ArgumentParser(prog="Forecast generator")
    parser.add_argument("command", choices=["summary", "detail"])
    args = parser.parse_args()
    if args.command == "summary":
        print_summary(timeseries, dates, targets)
    elif args.command == "detail":
        print_detail(timeseries, dates)


if __name__ == "__main__":
    main()
