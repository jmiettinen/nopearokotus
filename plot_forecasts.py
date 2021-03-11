from datetime import datetime
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fetch_data import fetch_vaccination_data
from models import current_usage, shots_for_all, third_dosage, half_dosage
from vaccination_forecast import forecast

pd.date_range("1/1/2000", periods=1000)


def plot_results(timeseries: Dict[str, List[int]], dates: List[datetime], output_filename: str) -> None:
    col_names: List[str] = []
    cols: List[List[int]] = []
    for k, v in timeseries.items():
        col_names.append(k)
        cols.append(v)
    cols = list(map(list, zip(*cols)))
    df = pd.DataFrame(cols, index=dates, columns=col_names)
    plot = df.plot()
    plot.get_figure().savefig(output_filename)


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
    os.makedirs("out")
    plot_results(timeseries, dates, "out/tmp.png")


if __name__ == "__main__":
    main()
