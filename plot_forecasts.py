from datetime import datetime
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure as fig
import seaborn as sns
import matplotlib.dates as mdates
from dateutil.rrule import MO as monday


def find_first_data_point_after(data: List[float], target: float) -> Optional[int]:
    datum: float
    for index, datum in enumerate(data):
        if datum > target:
            return index
    return None


def plot_days_until_target(timeseries: Dict[str, List[float]],
                           dates: List[datetime],
                           target: int,
                           target_name: str,
                           axes) -> None:
    pass


def plot_results(timeseries: Dict[str, List[float]],
                 dates: List[datetime],
                 targets_and_labels: List[Tuple[str, int]] = []) -> fig.Figure:
    sns.set_theme(style="darkgrid")
    col_names: List[str] = []
    cols: List[List[float]] = []
    for k, v in timeseries.items():
        col_names.append(k)
        cols.append(v)
    for k, v in targets_and_labels:
        col_names.append(k)
        tmp = [v for x in range(len(cols[0]))]
        cols.append(tmp)

    cols_t: List[List[float]] = list(map(list, zip(*cols)))
    df = pd.DataFrame(cols_t, index=dates, columns=col_names)
    fig, ax = plt.subplots(figsize=(10, 5))
    locator = mdates.WeekdayLocator(byweekday=monday)
    ax.xaxis.set_major_locator(locator)
    # XXX Fix to show Finnish months and week numbers!
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set_yticks([1_000_000, 2_000_000, 3_000_000, 4_000_000, 5_000_000, 6_000_000])
    ax.set_yticklabels(['1', '2', '3', '4', '5', '6'])
    sns.lineplot(ax=ax, data=df, palette="tab10", linewidth=1.5, legend=col_names + [x[0] for x in targets_and_labels])
    ax.set_xlabel("Aika")
    ax.set_ylabel("Rokotettu väestö (miljoonaa)")
    return ax.figure


def fetch_data_for_main():
    from fetch_data import fetch_vaccination_data
    from models import current_usage, shots_for_all, third_dosage, smaller_dosage, targets, facts
    from vaccination_forecast import forecast

    data = fetch_vaccination_data()
    parameters = [
        current_usage,
        smaller_dosage,
        third_dosage,
        shots_for_all
    ]
    timeseries: Dict[str, List[float]] = {}
    dates: List[datetime] = []
    for param in parameters:
        forecasted_data = forecast(180, facts["population"]["all"], data, second_dosage_interval=param["second_dose"],
                                   pfizer_multiplier=param["pfizer"], moderna_multiplier=param["moderna"],
                                   az_multiplier=param["az"])
        timeseries[param["name"]] = [x.amount for x in forecasted_data]
        dates = [x.date for x in forecasted_data]
    return timeseries, dates, targets


def main():
    timeseries, dates, targets = fetch_data_for_main()
    import os
    os.makedirs("out", exist_ok=True)
    target_list = [(x["name"], x["target"]) for x in targets]
    fig = plot_results(timeseries, dates, target_list)
    fig.savefig("out/tmp.png", dpi=300)


if __name__ == "__main__":
    main()
