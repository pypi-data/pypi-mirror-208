import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew

__all__ = [
    "tran_col",
    "extract_stat_feature",
    "MethodObject"
]

def tran_col(data, col):    
    if type(col) is not list:
        col = [col]

    data_col_len = len(data.columns)

    # str col index to int col index
    for i, c in enumerate(col):
        if type(c) is str:
            if c not in data.columns:
                raise ValueError(f"Column {c} not in data")
            col[i] = data.columns.get_loc(c)
        elif type(c) is int:
            if c >= data_col_len:
                raise ValueError(f"Column index {c} out of range")
        else:
            raise TypeError(f"Column {c} is not str or int")

    return col

def extract_stat_feature(data : pd.DataFrame, col : int):
    timeseries = data.iloc[:, col].to_numpy()

    # 时域特征
    max_val = np.max(timeseries)
    min_val = np.min(timeseries)
    peak_val = np.max(np.abs(timeseries))
    mean_val = np.mean(timeseries)
    var_val = np.var(timeseries)
    rms_val = np.sqrt(np.mean(np.square(timeseries)))

    crest_factor = peak_val / rms_val  # 峰值因子
    pulse_factor = peak_val / np.mean(np.abs(timeseries))  # 脉冲因子
    margin_factor = peak_val / np.mean(np.sqrt(np.abs(timeseries)))**2  # 裕度因子
    kurtosis_factor = kurtosis(timeseries)  # 峭度因子
    shape_factor = rms_val / mean_val  # 波形因子
    skewness_factor = skew(timeseries)  # 偏度

    # 频域特征
    freq_spectrum = np.fft.fft(timeseries)
    power_spectrum = np.square(np.abs(freq_spectrum))
    freq = np.fft.fftfreq(timeseries.shape[-1])
    freq = freq[:int(len(freq) / 2)]
    power_spectrum = power_spectrum[:int(len(power_spectrum) / 2)] / power_spectrum.sum()

    cent_freq = np.sum(power_spectrum * freq)  # 重心频率
    rms_freq = np.sum(power_spectrum * np.square(freq))  # 均方频率
    rms_freq = np.sqrt(rms_freq)
    var_freq = np.sum(power_spectrum * np.square(freq - cent_freq))  # 频率方差
    std_freq = np.sqrt(var_freq)  # 频率标准差

    # 返回所有特征值
    features_dict = {'max_val': max_val,
                     'min_val': min_val,
                     'peak_val': peak_val,
                     'mean_val': mean_val,
                     'var_val': var_val,
                     'rms_val': rms_val,
                     'crest_factor': crest_factor,
                     'pulse_factor': pulse_factor,
                     'margin_factor': margin_factor,
                     'kurtosis_factor': kurtosis_factor,
                     'shape_factor': shape_factor,
                     'skewness_factor': skewness_factor,
                     'cent_freq': cent_freq,
                     'rms_freq': rms_freq,
                     'var_freq': var_freq,
                     'std_freq': std_freq}
    return features_dict

class MethodObject:
    def __init__(self, data : pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs):
        # should define self._required_args in subclass before super().__init__()
        self._run_once = False # should be set to True after super().__init__()
        self._args_check_and_set(kwargs)

        if analysis:
            print("analysis mode unsupport for now")
        
        self.data = data
        self.inplace = inplace
        self.target_col = tran_col(data, target_col)
    
    def _args_check_and_set(self, kwargs):
        if not hasattr(self, "_required_args"):
            return 
        
        for arg in self._required_args:
            if arg not in kwargs.keys():
                raise ValueError(f"Argument {arg} is required")
            setattr(self, arg, kwargs[arg])
    
    def man(self):
        raise NotImplementedError

    def run(self):
        if self.inplace is False:
            self.data = self.data.copy(deep=True)
        
        if self._run_once is False:
            for col in self.target_col:
                self.real_run(col)
        else:
            self.real_run(self.target_col)

        return self.data

    def real_run(self, target_col):
        raise NotImplementedError