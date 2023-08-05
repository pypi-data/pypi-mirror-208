from .denoise_object import DenoiseObject

import pandas as pd
import numpy as np

from PyEMD import EMD


class EmdDenoise(DenoiseObject):
    _required_args = ["p"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["p"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        emd = EMD()
        imfs = emd(self.data.iloc[:, target_col].to_numpy())

        emd_out = np.zeros_like(imfs[0])
        for i in range(np.shape(imfs)[0] - self.p):
            emd_out += imfs[i + self.p]

        self.data.iloc[:, target_col] = emd_out
