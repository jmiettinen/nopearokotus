from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from fetch_data import fetch_vaccination_data
from models import Target, first_doses_first, WeeklyDeliveryDate, _far_future
from models import current_usage, shots_for_all, third_dosage, targets, facts, no_az_usage
from dateutil.parser import parse

from vaccination_forecast import forecast


def fetch_data_for_main(forecast_length: int = 270, parameters=(
        shots_for_all,
        third_dosage,
        first_doses_first,
        current_usage,
        no_az_usage)) -> Tuple[Dict[str, List[float]], List[datetime], List[Target]]:
    from fetch_data import fetch_vaccination_data

    data = fetch_vaccination_data()

    timeseries: Dict[str, List[float]] = {}
    dates: List[datetime] = []
    for param in parameters:
        forecasted_data = forecast(forecast_length, facts["population"]["all"], data, second_shot_portion=0.5,
                                   second_shot_interval=param["second_dose"], pfizer_multiplier=param["pfizer"],
                                   moderna_multiplier=param["moderna"], az_multiplier=param["az"])
        timeseries[param["name"]] = [float(x.amount) for x in forecasted_data]
        dates = [x.date for x in forecasted_data]
    return timeseries, dates, targets


def find_target_date(vaccinated: List[float], target: int, dates: List[datetime]) -> Optional[datetime]:
    for i in range(len(vaccinated)):
        if vaccinated[i] >= target:
            return dates[i]
    return None


def print_summary(timeseries: Dict[str, List[float]], dates: List[datetime], targets: List[Target]) -> None:
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


def date_string_to_datetime(date_string: str) -> datetime:
    return parse(f"{date_string}T00:00:00.000Z")


def deliveries_to_proper_model(delivery_data: List[Dict[str, Any]]) -> Dict[str, List[WeeklyDeliveryDate]]:
    res: Dict[str, List[WeeklyDeliveryDate]] = {}
    no_end_date = _far_future
    for delivery in delivery_data:
        end_date = delivery.get("end", None)
        if end_date is None:
            end_date = no_end_date
        else:
            end_date = date_string_to_datetime(end_date)
        dd: WeeklyDeliveryDate = WeeklyDeliveryDate(
            rate=delivery["rate"],
            start=date_string_to_datetime(delivery["start"]),
            end=end_date
        )
        delivery_list = res.get(delivery["name"], [])
        delivery_list.append(dd)
        res[delivery["name"]] = delivery_list
    return res


def forecast_for_models(forecast_length: int, models: List[Dict[str, Any]]) -> Tuple[Dict[str, List[float]], List[datetime], List[Target]]:
    data = fetch_vaccination_data()
    models_and_deliveries: List[Tuple[Dict[str, Any], Dict[str, List[WeeklyDeliveryDate]]]] = [
        ({"name": x["name"]} | x["parameters"], deliveries_to_proper_model(x["deliveries"])) for x in models
    ]
    timeseries: Dict[str, List[float]] = {}
    dates: List[datetime] = []
    for param, deliveries in models_and_deliveries:
        forecasted_data = forecast(forecast_length, facts["population"]["all"], data, second_shot_portion=0.5,
                                   second_shot_interval=param["second_dose"], pfizer_multiplier=param["pfizer"],
                                   moderna_multiplier=param["moderna"], az_multiplier=param["az"],
                                   vaccine_deliveries=deliveries)
        timeseries[param["name"]] = [float(x.amount) for x in forecasted_data]
        dates = [x.date for x in forecasted_data]

    return timeseries, dates, targets


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="Forecast generator")
    parser.add_argument("--model", help="Models to use instead of the default models")
    parser.add_argument("command", choices=["summary", "detail"])
    args = parser.parse_args()
    if args.model:
        with open(args.model) as json_file:
            import json
            models_as_dict = json.load(json_file)
        timeseries, dates, targets = forecast_for_models(400, models_as_dict)
    else:
        timeseries, dates, targets = fetch_data_for_main(400)

    if args.command == "summary":
        print_summary(timeseries, dates, targets)
    elif args.command == "detail":
        print_detail(timeseries, dates)


if __name__ == "__main__":
    main()
