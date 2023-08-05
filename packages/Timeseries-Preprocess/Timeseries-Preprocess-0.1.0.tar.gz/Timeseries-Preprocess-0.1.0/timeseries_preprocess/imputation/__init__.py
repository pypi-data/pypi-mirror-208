from .imputation_object import *

from .mean_imputation import *
from .median_imputation import *
from .mode_imputation import *
from .fixed_value_imputation import *
from .forward_imputation import *
from .backward_imputation import *
from .moving_avg_imputation import *
from .weighted_moving_avg_imputation import *
from .interpolate_imputation import *

from .knn_imputation import *
from .missing_forest_imputation import *

__all__ = [
    'imputation_object',
    'mean_imputation',
    'median_imputation',
    'mode_imputation',
    'fixed_value_imputation',
    'forward_imputation',
    'backward_imputation',
    'moving_avg_imputation',
    'weighted_moving_avg_imputation',
    'interpolate_imputation',
    'knn_imputation',
    'missing_forest_imputation',
]

if __name__ == '__main__':
    data = pd.DataFrame({'a': [1, np.nan, 3, np.nan, 5, np.nan],
                            'b': [1, np.nan, np.nan, 4, 5, 6],
                            'c': [1, np.nan, 2, np.nan, np.nan, np.nan],})
