from .denoise_object import DenoiseObject

import pandas as pd


class MovingMedianDenoise(DenoiseObject):
    _required_args = ["window"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["window"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        self.data.iloc[:, target_col] = (
            self.data.iloc[:, target_col]
            .rolling(window=self.window, center=True)
            .median()
        )

