from timeseries_preprocess.utils import MethodObject

import pandas as pd


class OutlierObject(MethodObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis, **kwargs)
        self.outliers = {}