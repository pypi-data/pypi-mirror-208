from .denoise_object import DenoiseObject

import pandas as pd
import numpy as np


class AdaptiveDenoise(DenoiseObject):
    _required_args = ["window", "threshold"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["window", "threshold"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        length = self.data.shape[0]
        pad_left = (self.window - 1) // 2
        pad_right = self.window - 1 - pad_left
        data_col = self.data.iloc[:, target_col].to_numpy()
        padded_data_col = np.pad(data_col, pad_width=pad_left, mode="edge")

        output = np.zeros_like(data_col)

        for i in range(length):
            local_mean = np.mean(padded_data_col[i : i + self.window])
            local_var = np.var(padded_data_col[i : i + self.window])
            weight = 1.0 if local_var < self.threshold else self.threshold / local_var
            output[i] = (1 - weight) * data_col[i] + weight * local_mean

        self.data.iloc[:, target_col] = output
