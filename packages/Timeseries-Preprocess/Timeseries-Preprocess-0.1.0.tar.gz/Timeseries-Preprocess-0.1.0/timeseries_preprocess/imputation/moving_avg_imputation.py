from .imputation_object import ImputationObject

import pandas as pd


class MovingAvgImputation(ImputationObject):
    _required_args = ["window"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["window"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        self.data.iloc[:, target_col].fillna(
            self.data.iloc[:, target_col]
            .rolling(window=self.window, min_periods=1)
            .mean(),
            inplace=True,
        )
