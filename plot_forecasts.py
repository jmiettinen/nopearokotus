from datetime import datetime
from typing import List, Dict, Tuple, Optional

import matplotlib.dates as mdates
import matplotlib.figure as figure
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dateutil.rrule import MO as MONDAY
from seaborn import FacetGrid


def find_first_data_point_after(data: List[float], target: float) -> Optional[int]:
    datum: float
    for index, datum in enumerate(data):
        if datum > target:
            return index
    return None


def plot_days_until_target(timeseries: Dict[str, List[float]],
                           dates: List[datetime],
                           labels_and_targets: List[Tuple[str, int]] = []) -> figure.Figure:
    first_date = dates[0]
    dosage = []
    days_past_list = []
    label_list = []
    for series_name, series in timeseries.items():
        for label, target in labels_and_targets:
            days_past = (dates[find_first_data_point_after(series, target)] - first_date).days
            dosage.append(series_name)
            days_past_list.append(days_past)
            label_list.append(label)
    df = pd.DataFrame(data={
        "dosage": dosage,
        "days": days_past_list,
        "target": label_list
    })
    grid: FacetGrid = sns.catplot(col="target", y="days", x="dosage", kind="bar", data=df, height=4, aspect=1.8, legend=True)
    grid.set_axis_labels("Käytäntö", "Päivää")
    grid.set_titles("Tavoite: {col_name}")
    for row, name in enumerate(grid.col_names):
        # Hackety hackety hack to find the relevant data to annotate results
        treatment_data = df.query(f"target == '{name}'")
        ax = grid.facet_axis(0, row)
        for i, days in enumerate(treatment_data["days"]):
            ax.annotate(text=str(days), xy=(i, days), xycoords='data', xytext=(0, 5), textcoords='offset points')

    return grid.fig


def plot_results(timeseries: Dict[str, List[float]],
                 dates: List[datetime],
                 labels_and_targets: List[Tuple[str, int]] = []) -> figure.Figure:
    sns.set_theme(style="darkgrid")
    col_names: List[str] = []
    cols: List[List[float]] = []
    for k, v in timeseries.items():
        col_names.append(k)
        cols.append(v)
    for k, v in labels_and_targets:
        col_names.append(k)
        tmp = [v for x in range(len(cols[0]))]
        cols.append(tmp)

    cols_t: List[List[float]] = list(map(list, zip(*cols)))
    df = pd.DataFrame(cols_t, index=dates, columns=col_names)
    fig, ax = plt.subplots(figsize=(10, 5))
    locator = mdates.WeekdayLocator(byweekday=MONDAY)
    ax.xaxis.set_major_locator(locator)
    # XXX Fix to show Finnish months and week numbers!
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set_yticks([1_000_000, 2_000_000, 3_000_000, 4_000_000, 5_000_000, 6_000_000])
    ax.set_yticklabels(['1', '2', '3', '4', '5', '6'])
    sns.lineplot(ax=ax, data=df, palette="tab10", linewidth=1.5, legend=col_names + [x[0] for x in labels_and_targets])
    ax.set_xlabel("Aika")
    ax.set_ylabel("Rokotettu väestö (miljoonaa)")
    return ax.figure


def fetch_data_for_main():
    from fetch_data import fetch_vaccination_data
    from models import current_usage, shots_for_all, third_dosage, smaller_dosage, targets, facts
    from vaccination_forecast import forecast

    data = fetch_vaccination_data()
    from models import no_az_usage
    parameters = [
        no_az_usage,
        current_usage,
        smaller_dosage,
        third_dosage,
        shots_for_all
    ]
    timeseries: Dict[str, List[float]] = {}
    dates: List[datetime] = []
    for param in parameters:
        forecasted_data = forecast(270, facts["population"]["all"], data,
                                   second_shot_interval=param["second_dose"],
                                   second_shot_portion=0.4,
                                   pfizer_multiplier=param["pfizer"], moderna_multiplier=param["moderna"],
                                   az_multiplier=param["az"])
        timeseries[param["name"]] = [float(x.amount) for x in forecasted_data]
        dates = [x.date for x in forecasted_data]
    return timeseries, dates, targets


def main():
    timeseries, dates, targets = fetch_data_for_main()
    import os
    os.makedirs("out", exist_ok=True)
    target_list = [(x["name"], x["target"]) for x in targets]
    plot_results(timeseries, dates, target_list).savefig("out/tmp.png", dpi=300)
    plot_days_until_target(timeseries, dates, target_list).savefig("out/tmp_2.png", dpi=300)


if __name__ == "__main__":
    main()
