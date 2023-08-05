from .denoise import *
from .outlier import *
from .imputation import *
from .utils import *

import pandas as pd
import numpy as np
import copy

def _init_methods():
    methods = {
        'outlier': {
            'gesd_outlier' : gesd_outlier.GesdOutlier,
            'iqr_outlier' : iqr_outlier.IqrOutlier,
            'kmeans_outlier' : kmeans_outlier.KmeansOutlier,
            'dbscan_outlier' : dbscan_outlier.DbscanOutlier,
        },
        'denoise': {
            'moving_average' : moving_avg_denoise.MovingAvgDenoise,
            'moving_median_denoise' : moving_median_denoise.MovingMedianDenoise,
            'adaptive_denosie' : adaptive_denoise.AdaptiveDenoise,
            'fourier_denoise' : fourier_denoise.FourierDenoise,
            'emd_denoise' : emd_denoise.EmdDenoise,
            'eemd_denoise' : eemd_denoise.EemdDenoise,
            'ceemdan_denoise' : ceemdan_denoise.CeemdanDenoise,
            # 'ssa_denoise' : ssa_denoise.SsaDenoise,
        },
        'imputation': {
            'mean_imputation' : mean_imputation.MeanImputation,
            'median_imputation' : median_imputation.MedianImputation,
            'mode_imputation' : mode_imputation.ModeImputation,
            'fixed_value_imputation' : fixed_value_imputation.FixedValueImputation,
            'forward_imputation' : forward_imputation.ForwardImputation,
            'backward_imputation' : backward_imputation.BackwardImputation,
            'moving_avg_imputation' : moving_avg_imputation.MovingAvgImputation,
            'weighted_moving_avg_imputation' : weighted_moving_avg_imputation.WeightedMovingAvgImputation,
            'interpolate_imputation' : interpolate_imputation.InterpolateImputation,
            'knn_imputation' : knn_imputation.KnnImputation,
            'missing_forest_imputation' : missing_forest_imputation.MissingForestImputation,
        }
    }
    return methods

class TSPP:
    def __init__(self, data : pd.DataFrame = None, time_index : str or int = None):
        if data is not None:
            self.data = data.copy(deep=True)

            if time_index is not None:
                self.set_time_index(time_index)

        self.methods = _init_methods()

        self.pipeline = []

    def init_data(self, data : pd.DataFrame, time_index : str or int = None):
        if len(self.pipeline) > 0:
            raise Exception('Pipeline is not empty, please clear the pipeline first.')
        
        self.data = data.copy(deep=True)

        if time_index is not None:
            self.set_time_index(time_index)

    def set_time_index(self, time_index : str or int):
        if isinstance(time_index, str):
            # self.data[time_index] = pd.to_datetime(self.data[time_index], format='%Y-%m')
            self.data.set_index(time_index, inplace=True)
        elif isinstance(time_index, int):
            # self.data.iloc[:, time_index] = pd.to_datetime(self.data.iloc[:, time_index], format='%Y-%m')
            self.data.set_index(self.data.columns.values[time_index], inplace=True)
    
    class PipelineItem:
        def __init__(self, method : MethodObject, method_class, method_name, target_col, **kwargs):
            self.method = method
            self.method_class = method_class
            self.method_name = method_name
            self.target_col = target_col
            self.kwargs = copy.deepcopy(kwargs)

            self.in_data = method.data
            self.out_data = pd.DataFrame()

    def push_pipeline_item(self, method_class, method_name, target_col, **kwargs):
        method = self.methods[method_class][method_name](self.data, target_col, inplace=True, **kwargs)
        self.pipeline.append(self.PipelineItem(method, method_class, method_name, target_col, **kwargs))

    def insert_pipeline_item(self, idx, method_class, method_name, target_col, **kwargs):
        method = self.methods[method_class][method_name](self.data, target_col, inplace=True, **kwargs)
        self.pipeline.insert(idx, self.PipelineItem(method, method_class, method_name, target_col, **kwargs))

    def del_pipline_item(self, idx):
        self.pipeline.pop(idx)

    def clean_pipeline(self):
        self.pipeline = []

    def run_method(self, method_idx, data):
        item = self.pipeline[method_idx]
        item.method.in_data = data.copy(deep=True)
        item.method.data = data
        item.method.run()
        item.out_data = item.method.data.copy(deep=True)

        return item.method.data

    def run(self):
        pre_data = self.data.copy(deep=True)
        for idx in range(len(self.pipeline)):
            pre_data = self.run_method(idx, pre_data)

    def print_pipeline(self):
        for idx, item in enumerate(self.pipeline):
            print(f'{idx}. {item.method_class}.{item.method_name}\tapply column {item.target_col}\targs {item.kwargs}')

    def print_aviable_methods(self):
        for method_class in self.methods:
            print(f'{method_class}:')
            for method_name in self.methods[method_class]:
                print(f'\t{method_name}')
