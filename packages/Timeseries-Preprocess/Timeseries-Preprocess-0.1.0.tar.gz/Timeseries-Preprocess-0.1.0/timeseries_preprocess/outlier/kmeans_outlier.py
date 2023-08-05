from .outlier_object import OutlierObject

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


class KmeansOutlier(OutlierObject):
    _required_args = ["n_clusters", "max_outlier"]
    
    def __init__(
        self, data: pd.DataFrame, target_col, inplace=False, analysis=False, **kwargs
    ):
        self._required_args = ["n_clusters", "max_outlier"]
        super().__init__(data, target_col, inplace, analysis, **kwargs)
        self._run_once = True

    def real_run(self, target_col):
        data = self.data.iloc[:, target_col]

        n_clusters = self.n_clusters
        max_outlier = self.max_outlier

        kmeans = KMeans(n_clusters=n_clusters).fit(data)

        distances = []
        for i in range(n_clusters):
            cluster_center = kmeans.cluster_centers_[i]
            cluster_indices = np.where(kmeans.labels_ == i)
            cluster_data = data.iloc[cluster_indices]
            distance = np.linalg.norm(cluster_data - cluster_center, axis=1)
            distances.extend(distance)

        distances = np.array(distances)
        outliers = np.argsort(distances)[-max_outlier:]

        if self._run_once:
            self.outliers = outliers
        else:
            self.outliers[target_col] = outliers
