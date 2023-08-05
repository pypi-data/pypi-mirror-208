from .outlier_object import OutlierObject

import pandas as pd
import numpy as np


class IqrOutlier(OutlierObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        data = self.data.iloc[:, target_col].to_numpy()

        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = np.where((data > upper_bound) | (data < lower_bound))[0]

        if self._run_once:
            self.outliers = outliers
        else:
            self.outliers[target_col] = outliers
