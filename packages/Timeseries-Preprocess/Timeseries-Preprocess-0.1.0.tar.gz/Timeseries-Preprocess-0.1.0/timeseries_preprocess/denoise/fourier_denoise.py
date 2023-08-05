from .denoise_object import DenoiseObject

import pandas as pd
import numpy as np


class FourierDenoise(DenoiseObject):
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        super().__init__(data, target_col, inplace, analysis, **kwargs)

    def real_run(self, target_col):
        fft = np.fft.fft(self.data.iloc[:, target_col].to_numpy())

        psd = fft * np.conj(fft) / len(fft)

        fft = np.where(psd < 100, 0, fft)

        # Reconstruct the signal using the filtered wavelet transform.
        self.data.iloc[:, target_col] = np.fft.ifft(fft)
