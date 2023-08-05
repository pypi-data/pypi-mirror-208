from .imputation_object import ImputationObject

import pandas as pd
from sklearn.impute import KNNImputer


class KnnImputation(ImputationObject):
    _required_args = ["k"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["k"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)
        self._run_once = True

    def real_run(self, target_col):
        imputer = KNNImputer(n_neighbors=self.k)

        knn_data = self.data.copy(deep=True)
        knn_data = imputer.fit_transform(knn_data)

        self.data.iloc[:, target_col] = knn_data[:, target_col]
