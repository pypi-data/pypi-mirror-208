from .imputation_object import ImputationObject

import pandas as pd


class MeanImputation(ImputationObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        self.data.iloc[:, target_col].fillna(
            self.data.iloc[:, target_col].mean(), inplace=True
        )

