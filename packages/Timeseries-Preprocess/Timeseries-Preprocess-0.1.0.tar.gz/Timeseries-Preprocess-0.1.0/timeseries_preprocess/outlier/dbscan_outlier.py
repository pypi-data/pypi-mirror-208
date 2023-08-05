from .outlier_object import OutlierObject

import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np


class DbscanOutlier(OutlierObject):
    _required_args = ["eps", "min_samples"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["eps", "min_samples"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)
        self._run_once = True

    def real_run(self, target_col):
        data = self.data.iloc[:, target_col]

        eps = self.eps
        min_samples = self.min_samples

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(data)

        outliers = np.where(dbscan.labels_ == -1)[0]

        if self._run_once:
            self.outliers = outliers
        else:
            self.outliers[target_col] = outliers
