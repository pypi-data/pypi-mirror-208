from .imputation_object import ImputationObject

import pandas as pd

import sklearn.neighbors._base
import sys

sys.modules["sklearn.neighbors.base"] = sklearn.neighbors._base
from missingpy import MissForest


class MissingForestImputation(ImputationObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis, **kwargs)

        self._run_once = True

    def real_run(self, target_col):
        imputer = MissForest()

        forest_data = self.data.copy(deep=True)
        forest_data = imputer.fit_transform(forest_data)

        self.data.iloc[:, target_col] = forest_data[:, target_col]

