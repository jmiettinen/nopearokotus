from datetime import datetime
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fetch_data import fetch_vaccination_data
from models import current_usage, shots_for_all, third_dosage, half_dosage, targets
from vaccination_forecast import forecast


def plot_results(timeseries: Dict[str, List[int]],
                 dates: List[datetime],
                 output_filename: str,
                 targets_and_labels: List[Tuple[str, int]] = []) -> None:
    col_names: List[str] = []
    cols: List[List[int]] = []
    for k, v in timeseries.items():
        col_names.append(k)
        cols.append(v)
    cols = list(map(list, zip(*cols)))
    df = pd.DataFrame(cols, index=dates, columns=col_names)
    plot = df.plot(ylim=[0, 6_000_000], figsize=(12, 8))
    plot.get_figure().savefig(output_filename, dpi=300)


def main():
    data = fetch_vaccination_data()
    parameters = [
        current_usage,
        half_dosage,
        third_dosage,
        shots_for_all
    ]
    timeseries: Dict[str, List[int]] = {}
    dates: List[datetime] = []
    for param in parameters:
        forecasted_data = forecast(180, data,
                                   second_dosage_interval=param["second_dose"],
                                   pfizer_multiplier=param["pfizer"],
                                   moderna_multiplier=param["moderna"]
                                   )
        timeseries[param["name"]] = [x.amount for x in forecasted_data]
        dates = [x.date for x in forecasted_data]

    import os
    os.makedirs("out", exist_ok=True)
    target_list = [(x["name"], x["target"]) for x in targets]
    plot_results(timeseries, dates, "out/tmp.png", target_list)


if __name__ == "__main__":
    main()
