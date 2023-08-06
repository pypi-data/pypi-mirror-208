import joblib
import numpy as np
import pandas as pd

from . import PACKAGEDIR

MPLSTYLE = PACKAGEDIR / "data" / "flarespy.mplstyle"
RFC_MODEL = joblib.load(PACKAGEDIR / "data" / "model.dat")


def extract_features(x):
    abs_energy = np.dot(x, x)
    first_location_of_maximum = np.argmax(x) / len(x)

    abs_x = np.abs(x)
    s = np.sum(abs_x)
    mass_centralized = np.cumsum(abs_x) / s
    mass_center = (np.argmax(mass_centralized >= 0.5) + 1) / len(x)

    kurtosis = pd.Series.kurtosis(pd.Series(x))
    length = len(x)
    maximum = np.max(x)
    root_mean_square = np.sqrt(np.mean(np.square(x)))
    skewness = pd.Series.skew(pd.Series(x))
    standard_deviation = np.std(x)

    return pd.DataFrame(
        {
            "flux__abs_energy": [abs_energy],
            "flux__first_location_of_maximum": [first_location_of_maximum],
            "flux__index_mass_quantile__q_0.5": [mass_center],
            "flux__kurtosis": [kurtosis],
            "flux__length": [length],
            "flux__maximum": [maximum],
            "flux__root_mean_square": [root_mean_square],
            "flux__skewness": [skewness],
            "flux__standard_deviation": [standard_deviation],
        }
    )


def extend(time, flux, t_start, t_stop, t_max_extend, n_sigma=1, n_left=1, n_right=1, mode=1):
    indexes_range = np.nonzero((time >= t_start - t_max_extend) & (time <= t_stop + t_max_extend))[0]
    i_start = np.nonzero(time == t_start)[0][0]
    i_stop = np.nonzero(time == t_stop)[0][0]

    def condition_left(index):
        if mode == 1:
            return (flux[index - n_left : index] > n_sigma).any()
        elif mode == -1:
            return (flux[index - n_left : index] < n_sigma).any()
        else:
            raise ValueError("mode must be 1 or -1")

    def condition_right(index):
        if mode == 1:
            return (flux[index + 1 : index + 1 + n_right] > n_sigma).any()
        elif mode == -1:
            return (flux[index + 1 : index + 1 + n_right] < n_sigma).any()
        else:
            raise ValueError("mode must be 1 or -1")

    # Extend left
    while condition_left(i_start) and i_start > indexes_range[0]:
        i_start -= 1
        if i_start < n_left:
            i_start = 0
            break
    i_start = max(0, i_start - 1, indexes_range[0])

    # Extend right
    while condition_right(i_stop) and i_stop < indexes_range[-1]:
        i_stop += 1
        if i_stop + 1 + n_right > time.size:
            i_stop = time.size - 1
            break
    i_stop = min(time.size - 1, i_stop + 1, indexes_range[-1])

    return time[i_start], time[i_stop]


def find_consecutive(indexes, n_consecutive, gap=1, data=None):
    if data is None:
        grouped_data = np.split(indexes, np.nonzero(np.diff(indexes) > gap)[0] + 1)
    else:
        grouped_data = np.split(indexes, np.nonzero(np.diff(data[indexes]) > gap)[0] + 1)

    grouped_consecutive_data = [x for x in grouped_data if x.size >= n_consecutive]

    if grouped_consecutive_data:
        i_start_array = np.array([x[0] for x in grouped_consecutive_data], dtype=int)
        i_stop_array = np.array([x[-1] for x in grouped_consecutive_data], dtype=int)
        return i_start_array, i_stop_array
    else:
        return np.array([]), np.array([])
