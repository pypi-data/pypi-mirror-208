from .imputation_object import ImputationObject

import pandas as pd
import numpy as np


class WeightedMovingAvgImputation(ImputationObject):
    _required_args = ["window"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["window"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        weights = np.exp(np.linspace(-1.0, 0.0, self.window))
        weights /= weights.sum()

        self.data.iloc[:, target_col].fillna(
            self.data.iloc[:, target_col]
            .rolling(window=self.window, min_periods=1)
            .apply(lambda x: np.average(x, weights=weights[:len(x)])),
            inplace=True,
        )
