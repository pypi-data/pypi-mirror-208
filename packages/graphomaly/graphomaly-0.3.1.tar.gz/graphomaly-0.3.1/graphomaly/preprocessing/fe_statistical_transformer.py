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

from .fe_base.statistical_features import GroupStatisticalFeatures
from .fe_base.statistical_features import BASE_UNITS, ALL_STATS_FEATS


class GroupStatisticalFeatTransformer(TransformerMixin, BaseEstimator):
    """ Computes statistical features given certain groups 
    delimited by the second column, on the latter columns' values, of indices [2:].
    The results are time differences between 2 consecutive entries,
    expressed in time units.
    Please refer to the
    :class:`~preprocessing.fe_base.statistical_features.GroupStatisticalFeatures` class
    for basic examples.

    Assumes that the first column of X is np.datetime64 and
    the second column contains values that can be split
    into groups (e.g., user ID), and
    produces historical time-related feature.
    The following columns will contain the features on which the feature_list
    computations will be applied, after being grouped.

    This is a Scikit-learn compatible Wrapper of the
    :class:`~preprocessing.fe_base.statistical_features.GroupStatisticalFeatures` class.

    Parameters
    ----------
    feature_list : 'auto' or array-like of str, default='auto'
        List of features to be computed for each numeric column.
        Possible values:

        * 'auto' : Compute all time features liste below.
        * The available options are:

            - 'max': the maximum value
            - 'min': the minimum value
            - 'mean': the mean value
            - 'std': the standard deviation
            - 'median': the median value
            - 'quant_0.25': the value at 25 percentile
            - 'quant_0.75': the value at 75 percentile
            - 'count': the number of samples from the period.

    units : list of str, default=['1D', '7D', '30D', '60D', '90D', '1M', '2M', '3M']
        A list containing string pandas offsets (see
        `Pandas doc <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_),
        plus 'M' that means a calendaristic month (different from pandas).

    group_suffix : str, default=''
        A suffix to be appended to the resulting columns in order to
        differentiate between the same features computed for different
        group ids.
        When default, it will contain the suffix 'ID'. 
            
    engine : {'cython', 'numba'}, default='cython'
        - 'cython': Runs rolling apply through C-extensions from cython.
        - 'numba': Runs rolling apply through JIT compiled code from numba.
        

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

    """

    def __init__(
        self, *, feature_list="auto", units="auto", group_suffix="", engine="cython"
    ):

        self.date_column = "date"
        self.groupby_column = "ID"
        self.feature_list = feature_list
        self.units = units
        self.group_suffix = group_suffix
        self.engine = engine

    def fit(self, X, y=None):
        """
        Prepare applying GroupStatisticalFeatTransformer to `X`.

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

        # Check if feature_list is of the correct type
        if isinstance(self.feature_list, str):
            if self.feature_list == "auto":
                self.feature_list = ALL_STATS_FEATS
            else:
                raise ValueError(
                    "Invalid value for feature_list. Allowed string value is 'auto'."
                )
        elif not isinstance(self.feature_list, collections.abc.Iterable):
            raise ValueError(
                "Invalid value for feature_list. "
                "feature_list must be 'auto' or array-like of str."
            )

        # Check if units is of the correct type
        if isinstance(self.units, str):
            if self.units == "auto":
                self.units = BASE_UNITS
            else:
                raise ValueError(
                    "Invalid value for units. Allowed string value is 'auto'."
                )
        elif not isinstance(self.units, collections.abc.Iterable):
            raise ValueError(
                "Invalid value for units. "
                "units must be 'auto' or an array-like of str."
            )

        # Check if engine is of the correct type
        if self.engine is not "cython" and self.engine is not "numba":
            raise ValueError(
                "Invalid value for engine. "
                "Allowed string values as 'cython' or 'numba'."
            )

        self.groupstatfeat_obj = GroupStatisticalFeatures(
            date_column=self.date_column,
            group_by=self.groupby_column,
            units=self.units,
            group_suffix=self.group_suffix,
            engine=self.engine,
            features=self.feature_list,
            col_names=None,  # will be extracted later
        )

        self.feature_names_in_ = np.asarray(
            [(feat, unit) for feat in self.feature_list for unit in self.units]
        )
        self.n_features_in_ = self.feature_names_in_.shape[0]
        return self

    def transform(self, X):
        """Transform the columns [2:] of `X` to the selected features,
        considering the timestamp in column 0 and the ID for the group_by
        clause in column 1.

        Parameters
        ----------
        X : array of shape (n_samples, n_features)
            The input samples, having the time column first,
            and the group IDs column, second.

        Returns
        -------
        X_r : array of shape (n_samples, n_transformed_features)
            The input samples with only the transformed features.
        """

        df = pd.DataFrame(X)
        df.columns = df.columns.map(str)
        df.rename(
            columns={
                df.columns[0]: self.date_column,
                df.columns[1]: self.groupby_column,
            },
            inplace=True,
        )
        # Set the names of the columns on which to apply the feature_list
        self.groupstatfeat_obj.col_names = df.columns[2:].to_list()

        df, new_cols_names = self.groupstatfeat_obj.build_features(df)

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
