from .imputation_object import ImputationObject

import pandas as pd


class FixedValueImputation(ImputationObject):
    _required_args = ["value"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["value"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        self.data.iloc[:, target_col].fillna(self.value, inplace=True)
