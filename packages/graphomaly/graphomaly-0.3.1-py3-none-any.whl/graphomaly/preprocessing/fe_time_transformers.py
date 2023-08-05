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
from .fe_base.time_features import TimeFeatures, ALL_TIME_FEATS
from .fe_base.time_features import GroupHistoricalTimeFeatures


class TimeFeatTransformer(TransformerMixin, BaseEstimator):
    """ Creates several features based on timestamp column.

    Assumes that the first column of `X` is numpy.datetime64 and
    produces time-related features in several new columns.

    This is a Scikit-learn compatible Wrapper of the
    :class:`~preprocessing.fe_base.time_features.TimeFeatures` class.

    Parameters
    ----------
    feature_list : 'auto' or array-like of str, default='auto'
        Possible values:

        * 'auto' : Compute all time features.
        * The exhaustive list is:
            
            * 'day_of_year'
            * 'day_of_month'
            * 'day_of_week'
            * 'year'
            * 'month'
            * 'week'
            * 'hour'
            * 'minutes_of_hour'
            * 'minutes_of_day'

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.
    """

    def __init__(
        self, *, feature_list="auto",
    ):

        self.date_column = "date"
        self.feature_list = feature_list

    def fit(self, X, y=None):
        """
        Prepare applying TimeFeatTransformer to `X`.

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
                self.feature_list = ALL_TIME_FEATS
            else:
                raise ValueError(
                    "Invalid value for feature_list. Allowed string value is 'auto'."
                )
        elif not isinstance(self.feature_list, collections.abc.Iterable):
            raise ValueError(
                "Invalid value for feature_list. "
                "feature_list must be 'auto' or array-like of str."
            )

        if self.feature_list is "auto":
            self.feature_list = ALL_TIME_FEATS
        self.timefeat_obj = TimeFeatures(self.date_column, features=self.feature_list)

        self.feature_names_in_ = np.asarray(self.feature_list)
        self.n_features_in_ = self.feature_names_in_.shape[0]
        return self

    def transform(self, X):
        """Transform the first column of `X` to the selected features.

        Parameters
        ----------
        X : array of shape (n_samples, n_features)
            The input samples, having the time column first.

        Returns
        -------
        X_r : array of shape (n_samples, n_transformed_features)
            The input samples with only the transformed features.
        """

        df = pd.DataFrame(X)
        df.rename(columns={df.columns[0]: self.date_column}, inplace=True)
        df, new_cols_names = self.timefeat_obj.build_features(df)

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


class GroupHistTimeFeatTransformer(TransformerMixin, BaseEstimator):
    """ Compute historical time features given certain groups 
    delimited by the second column.
    The results are time differences between 2 consecutive entries,
    expressed in time units.
    Please refer to the
    :class:`~preprocessing.fe_base.time_features.GroupHistoricalTimeFeatures`
    class for basic examples.

    Assumes that the first column of `X` is numpy.datetime64 and
    the second column contains values that can be split
    into groups (e.g., user ID), and
    produces historical time-related features for each group 
    in several new columns.

    This is a Scikit-learn compatible Wrapper of the
    :class:`~preprocessing.fe_base.time_features.GroupHistoricalTimeFeatures` class.

    Parameters
    ----------
    units : list of str, default=['h', 'D']
        The units in which to compute the differences. Available units:
        'h' (hour), 's' (second), 'm' (minute), 'D' (day)

    group_suffix : str, default=''
        A suffix to be appended to the resulting columns in order to
        differentiate between the same features computed for different
        group ids.
        When default, it will contain the suffix 'ID'. 

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

    """

    def __init__(self, *, units=["h", "D"], group_suffix=""):

        self.date_column = "date"
        self.groupby_column = "ID"
        self.units = units
        self.group_suffix = group_suffix

    def fit(self, X, y=None):
        """
        Prepare applying GroupHistTimeFeatTransformer to X.

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

        # Check if units is of the correct type
        if not isinstance(self.units, collections.abc.Iterable):
            raise ValueError(
                "Invalid value for units. " "units must be an array-like of str."
            )

        self.grouphisttime_obj = GroupHistoricalTimeFeatures(
            self.date_column, self.groupby_column, self.units, self.group_suffix
        )

        self.feature_names_in_ = np.asarray(self.units)
        self.n_features_in_ = self.feature_names_in_.shape[0]
        return self

    def transform(self, X):
        """Transform the first column of X to the selected features.

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
        df.rename(
            columns={
                df.columns[0]: self.date_column,
                df.columns[1]: self.groupby_column,
            },
            inplace=True,
        )

        df, new_cols_names = self.grouphisttime_obj.build_features(df)

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
