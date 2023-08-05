from .outlier_object import OutlierObject

import pandas as pd
import numpy as np
from scipy.stats import t


class GesdOutlier(OutlierObject):
    _required_args = ["alpha", "max_outlier"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["alpha", "max_outlier"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        data = self.data.iloc[:, target_col].to_numpy()
        max_outlier = self.max_outlier
        alpha = self.alpha

        n = len(data)
        outliers = []

        if max_outlier is not None and max_outlier >= n:
            return outliers
        k = max_outlier or n - 1

        for i in range(k):
            mean = np.mean(data)
            std = np.std(data, ddof=1)
            max_outlier = np.max(np.abs(data - mean))
            max_outlier_idx = np.argmax(np.abs(data - mean))
            t_score = max_outlier / std

            t_dist = t.ppf(1 - alpha / (2 * (n - i)), n - i - 2)
            numerator = (n - i - 1) * np.sqrt(np.square(t_dist))
            denumerator = np.sqrt(n - i) * np.sqrt(n - i - 2 + np.square(t_dist))
            critical_value = numerator / denumerator
            if t_score > critical_value:
                outliers.append(max_outlier_idx)
            data = np.delete(data, max_outlier_idx)

        if self._run_once:
            self.outliers = outliers
        else:
            self.outliers[target_col] = outliers
