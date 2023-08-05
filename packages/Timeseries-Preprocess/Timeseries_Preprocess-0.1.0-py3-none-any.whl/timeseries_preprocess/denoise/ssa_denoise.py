from .denoise_object import DenoiseObject

import pandas as pd
import numpy as np

from scipy.linalg import hankel


class SsaDenoise(DenoiseObject):
    _required_args = ["p"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["p"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        data = self.data
        p = self.p

        length = data.shape[0]
        data_col = data.iloc[:, target_col].to_numpy()

        # Create the trajectory matrix
        trajectory = hankel(data_col[:p], data_col[p - 1 :])

        # Extract the principal components of the time series
        u, s, vh = np.linalg.svd(trajectory)

        # Extract the principal components of the time series
        principal_components = np.dot(u[:, :p], vh[:p, :])

        # Compute the residual error
        r = trajectory - principal_components

        denoised = np.diag(s[:p]).dot(r[:, :p].T).flatten() / p

        print(denoised.shape)

        data.iloc[:, target_col] = denoised
