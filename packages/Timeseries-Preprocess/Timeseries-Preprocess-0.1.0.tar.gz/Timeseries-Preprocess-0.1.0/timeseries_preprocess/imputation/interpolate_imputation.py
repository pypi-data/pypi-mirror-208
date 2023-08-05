from .imputation_object import ImputationObject

import pandas as pd


class InterpolateImputation(ImputationObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis=False, **kwargs)

    def real_run(self, target_col):
        self.data.iloc[:, target_col].interpolate(inplace=True)
