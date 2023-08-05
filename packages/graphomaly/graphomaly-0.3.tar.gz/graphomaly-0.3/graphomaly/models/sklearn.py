import sklearn.ensemble


class SklearnIsolationForest(sklearn.ensemble.IsolationForest):
    def __init__(self, n_estimators=500, **kwargs) -> None:
        super().__init__(n_estimators=n_estimators, **kwargs)

    def decision_function(self, X):
        # flip decision funciton sign to match PyOD convention
        return -super(SklearnIsolationForest, self).decision_function(X)

    def predict(self, X):
        # PyOD uses “0” to represent inliers and “1” to represent outliers.
        # Differently, scikit-learn returns “-1” for anomalies/outliers and “1” for inliers.
        # convert outputs from -1 (outlier) / 1 (inlier) to 0 (inlier) / 1 (outlier)
        return (-1 * super().predict(X) + 1) / 2
