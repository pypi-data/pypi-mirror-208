# Copyright (c) 2022 Paul Irofti <paul@irofti.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np
import pandas as pd
from dictlearn import DictionaryLearning
from sklearn.preprocessing import MinMaxScaler


class AnomalyDL(DictionaryLearning):
    """Dictionary Learning [DL1]_ model for Unsupervised Anomaly Detection [DL2]_

    Parameters
    ----------
    threshold : float, default=None
        The threshold used for anomalies selection. If None, the
        contamination is used to compute the threshold.

    contamination : float, default=0.1
        The contamination rate used for computing the reconstruction error
        threshold. Used if threshold is not set.

    Attributes
    ----------
    decision_scores_ : array-like of shape (n_samples,)
        The raw outlier scores for the training data. The anomalies have
        a larger error score.

    labels_ : list of int (0 or 1)
        The binary labels for the training data. 0 means inliers and 1 means
        outliers.

    threshold_ : float
        The threshold for the raw outliers scores.

    References
    ----------
    .. [DL1] B. Dumitrescu and P. Irofti, Dictionary Learning Algorithms and
           Applications, Springer, 2018. http://dx.doi.org/10.1007/978-3-319-78674-2
    .. [DL2] P. Irofti and A. Băltoiu,Unsupervised Dictionary Learning for
           Anomaly Detection, in International Traveling Workshop on Interactions
           Between Sparse Models and Technology, 2020, pp. 1--3
    """

    def __init__(
        self,
        threshold=None,
        contamination=None,
        **pparams,
    ):
        super().__init__(**pparams)

        # Fixed parameters 
        self.contamination = contamination
        self.threshold = threshold      # Fixed threshold parameter specified at instantiation, while threshold_ is the actual threshold to use
        self.classes = 2

        # Attributes estimated from data, ending with `_`
        # See here for a general discussion: https://scikit-learn.org/stable/developers/develop.html
        self.threshold_ = None          # Threshold set based on contamination level, if self.threshold is None, else equal to threshold.
        self.decision_scores_ = None
        self.labels_ = None

    def _estimate(self, X):
        codes = self.transform(X)
        preds = (self.D_.T @ codes.T).T
        return preds

    def predict_decision_scores(self, X_train):
        """Predict the reconstruction errors for the samples on which the model
        was trained. The anomalies have a larger error score.

        These scores are used to fit the scaler used by
        predict_proba() method.

        Parameters
        ----------
        X_train : array-like of shape (num_samples, num_features)
            The train samples.

        Returns
        -------
        ndarray of shape (num_samples, )
            The reconstruction error scores.
        """
        preds = self._estimate(X_train)

        self.decision_scores_ = self._compute_scores(X_train, preds)
        self.scaler = MinMaxScaler()
        self.scaler.fit(self.decision_scores_.reshape(-1, 1))

        if self.threshold is None:
            if self.contamination is None:
                self.threshold_ = np.mean(self.decision_scores_) + np.std(
                    self.decision_scores_
                )
            else:
                self.threshold_ = pd.Series(self.decision_scores_).quantile(
                    1 - self.contamination
                )
        else:
            self.threshold_ = self.threshold

        self.labels_ = (self.decision_scores_ > self.threshold_).astype("int")

        return self.decision_scores_

    def decision_function(self, X):
        """Predict the reconstruction errors for some samples.
        The anomalies have a larger error score.

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the scores.

        Returns
        -------
        ndarray of shape (num_samples, )
            The reconstruction error scores.
        """
        preds = self._estimate(X)
        return self._compute_scores(X, preds)

    def predict_proba(self, X, method="linear"):
        """Compute a distribution probability on the reconstuction errors
        predicted for the samples passed as parameter. The scores as
        normalized using a scaler fitted on the train scores, so the method
        predict_decision_scores() must be called after training the model
        in order to be able to compute the probabilities.

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the probabilities.

        method : {'linear'}, default='linear'
            The method used for score normalization. Only 'linear'
            supported at the moment.

        Returns
        -------
        ndarray of shape (num_samples, )
            The probabilities for each class (normal prob on dimension 0,
            anomaly prob on dimension 1).
        """
        if self.decision_scores_ is None:
            raise Exception(
                "Train scores weren't computed. Please call "
                "predict_decision_scores(), then retry."
            )

        scores = self.decision_function(X)
        probs = np.zeros([X.shape[0], self.classes])

        if method == "linear":
            probs[:, 1] = self.scaler.transform(scores.reshape(-1, 1)).squeeze()
            probs[:, 0] = 1 - probs[:, 1]

        else:
            raise ValueError(
                f"{method} is not a valid value for probability" "conversion."
            )

        return probs

    def fit(self, X, y=None):
        super().fit(X)

        self.predict_decision_scores(X)

        return self

    def predict(self, X):
        """Predict binary labels for the samples passed as parameter.

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the probabilities.

        Returns
        -------
        ndarray of shape (num_samples, )
            The probabilities for each class.
        """
        pred_score = self.decision_function(X)
        self.labels_ = (pred_score > self.threshold_).astype("int")
        return self.labels_

    def fit_predict(self, X, y=None):
        return self.fit(X, y).predict(X)

    @staticmethod
    def _compute_scores(X, Y):
        return np.sqrt(np.sum(np.square(Y - X), axis=1))

    # We need to get the params of both AnomalyDL and its parent, Dictionary Learning
    # Not done automatically, see: https://github.com/scikit-learn/scikit-learn/issues/13555
    def get_params(self, deep=True):

        # Get params of current class (AnomalyDL) using the built-in get_params()
        params = super(AnomalyDL, self).get_params()

        # Get params of parent class (DictionaryLearning) by temporarily instantiating a parent object
        all = vars(self)
        parent_keys = DictionaryLearning().get_params(self).keys()
        parent_params = {k: all[k] for k in parent_keys}

        # Return their union
        params.update(parent_params)
        return params