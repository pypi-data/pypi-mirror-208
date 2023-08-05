# Copyright (c) 2022 Stefania Budulan <stefania.budulan@tremend.com>
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


import collections
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin

from .fe_base.historical_features import DifferenceFeatures


class DifferenceFeatTransformer(TransformerMixin, BaseEstimator):
    """ Computes a new feature containing the difference between
    the values of the first 2 columns from the input.
    It can be used as a consequent step in a transformer Pipeline,
    after computing statistical values for a group, to extract the difference
    from the current value.
    
    Please refer to the :class:`~preprocessing.fe_base.historical_features.DifferenceFeatures`
    class for basic examples.

    This is a Scikit-learn compatible Wrapper of the
    :class:`~preprocessing.fe_base.historical_features.DifferenceFeatures` class,
    which can perform this operation on multiple tuples received as input.

    Parameters
    ----------
    first_col : str, default='col1'
        The name of the first column, used for creating the output
        column name.
        
    second_col : str, default='col2'
        The name of the second column, used for creating the output
        column name.

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

    """

    def __init__(self, *, first_col="col1", second_col="col2"):

        self.first_col = first_col
        self.second_col = second_col

    def fit(self, X, y=None):
        """
        Prepare applying DifferenceFeatTransformer to X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data.
        y : None
            Ignored. This parameter exists only for compatibility with
            :class:`~sklearn.pipeline.Pipeline`.

        Returns
        -------
        self
            The transformer.
        """

        # Check if the first_col is of the correct type
        if not isinstance(self.first_col, str):
            raise ValueError("Invalid value for first_col. first_col must be string.")

        # Check if the second_col is of the correct type
        if not isinstance(self.second_col, str):
            raise ValueError("Invalid value for second_col. second_col must be string.")

        self.diff_feat_obj = DifferenceFeatures([(self.first_col, self.second_col)])

        self.feature_names_in_ = np.asarray([self.first_col, self.second_col])
        self.n_features_in_ = self.feature_names_in_.shape[0]
        return self

    def transform(self, X):
        """Transform the first 2 columns, obtaining the
        difference between the values of the same instance.

        Parameters
        ----------
        X : array of shape (n_samples, n_features)
            The input samples, with the first 2 columns being numerical features.

        Returns
        -------
        X_r : array of shape (n_samples, n_transformed_features)
            The input samples with only the transformed features.
        """

        df = pd.DataFrame(X)
        df.rename(
            columns={df.columns[0]: self.first_col, df.columns[1]: self.second_col},
            inplace=True,
        )

        df, new_cols_names = self.diff_feat_obj.build_features(df)

        # Reset index to keep the initial order
        df.sort_index(inplace=True)

        self._feature_names_out = np.asarray(new_cols_names, dtype=object)
        return df[self._feature_names_out].values

    def get_feature_names_out(self, input_features=None):
        """Get output feature names for transformation.

        Parameters
        ----------
        input_features : default=None
            Input features.
            Unused. Kept for consistency.

            * `feature_names_in_` may be a longer list if some of the
              feature names were incorrect, being, therefore, ignored in
              transformation.
            * Otherwise, the `feature_names_in_` matches the feature_names_out.

        Returns
        -------
        feature_names_out : ndarray of str objects
            Transformed feature names.
        """
        return self._feature_names_out
