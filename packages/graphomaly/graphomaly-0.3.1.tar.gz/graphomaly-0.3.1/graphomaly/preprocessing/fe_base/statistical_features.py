# Copyright (c) 2021 Alexandra Bodirlau <alexandra.bodirlau@tremend.com>
# Copyright (c) 2021 Stefania Budulan <stefania.budulan@tremend.com>
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

import pandas as pd
import numpy as np
from tqdm import tqdm
import logging

from enum import Enum

BASE_UNITS = ["1D", "7D", "30D", "60D", "90D", "1M", "2M", "3M"]


class StatsFeats(Enum):
    MAX = "max"
    MIN = "min"
    MEAN = "mean"
    STD = "std"
    MEDIAN = "median"
    QUANTILE25 = "quant_0.25"
    QUANTILE75 = "quant_0.75"
    COUNT = "count"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


ALL_STATS_FEATS = list(map(lambda x: x.value, StatsFeats))


class GroupStatisticalFeatures:
    """Compute statistical features on groups.

    Parameters
    ----------
    group_by : str
        The column to group by.

    date_column : str
        The column containing the date, in numpy.datetime64 format.

    units : list of str, default=['1D', '7D', '30D', '60D', '90D', '1M', '2M', '3M']
        A list containing string pandas offsets (see
        `Pandas doc <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_),
        plus 'M' that means a calendaristic month (different from pandas).

    group_suffix : str, default=''
        A suffix to be append to all extra columns added for the current group.

    engine : {'cython', 'numba'}, default='cython'
        - 'cython': Runs rolling apply through C-extensions from cython.
        - 'numba': Runs rolling apply through JIT compiled code from numba.

    features : list of str, default=['max', 'min', 'mean', 'std', 'median', 'quant_0.25', 'quant_0.75', 'count']
        List of features to be computed. Available options are:

        - 'max': the maximum value
        - 'min': the minimum value
        - 'mean': the mean value
        - 'std': the standard deviation
        - 'median': the median value
        - 'quant_0.25': the value at 25 percentile
        - 'quant_0.75': the value at 75 percentile
        - 'count': the number of samples from the period.

    col_names : list of str
        List of columns in DataFrame to apply feature extraction on. The
        columns in DataFrame must have numerical type, otherwise an
        exception is raised.

    Attributes
    ----------
    name : str
        The name of the features computed by GroupStatisticalFeatures class.

    Examples
    --------
    Given a toy dataframe:

    >>> df = pd.DataFrame({'amount': [100, 50, 30],
                           'date': ['2021-09-27', '2021-09-28', '2021-09-27'],
                           'userID': [1, 1, 2]
                          })
    >>> df
        amount      date	 userID
    0	100	    2021-09-27	1
    1	50	    2021-09-28	1
    2	30	    2021-09-27	2

    To compute the minimum value for the 'amount' column from the day before
    the current date, for each sample of each user ID from column 'user_id',
    instantiate class GroupStatisticalFeatures as follows:

    >>> statFeats = GroupStatisticalFeatures(['amount'],
                                             date_column='date',
                                             group_by='userID',
                                             units=['1D'],
                                             features=['min'])

    Compute the statistical features:

    >>> preprocessed_df, new_columns = statFeats.build_features(df)

    The initial dataframe has a new column 'amount_min_1D_userID', which
    contains the minimum values from the previous day for each sample of
    each user ID.

    >>> preprocessed_df
        amount	date	    userID	amount_min_1D_userID
    0	100.0	2021-09-27	1	    0.0
    2	30.0	2021-09-27	2	    0.0
    1	50.0	2021-09-28	1	    100.0

    The list of the new columns added through feature engineering is
    returned in new_columns variable

    >>> new_columns
    ['amount_min_1D_userID']
    """

    def __init__(
        self,
        group_by,
        date_column,
        units=BASE_UNITS,
        group_suffix="",
        engine="cython",
        features=ALL_STATS_FEATS,
        col_names=None,
    ):

        self.df = None
        self.col_names = col_names
        self.group_by = group_by
        self.date_column = date_column
        self.units = units
        self.group_suffix = group_suffix if group_suffix != "" else str(group_by)[:8]
        self.engine = engine
        self.name = f"GroupStatsFeatures_{self.group_suffix}"

        self._all_features = {
            StatsFeats.MAX.value: self.max_features,
            StatsFeats.MIN.value: self.min_features,
            StatsFeats.MEAN.value: self.mean_features,
            StatsFeats.STD.value: self.std_features,
            StatsFeats.MEDIAN.value: self.median_features,
            StatsFeats.QUANTILE25.value: self.quantile_features(q=0.25),
            StatsFeats.QUANTILE75.value: self.quantile_features(q=0.75),
            StatsFeats.COUNT.value: self.count_features,
        }

        self._check_features(features)

    def max_features(self, rolled_df_col, col_name, unit):
        new_col_name = (
            f"{col_name}_{StatsFeats.MAX.value}_{unit}_" f"{self.group_suffix}"
        )
        return new_col_name, rolled_df_col.max()

    def min_features(self, rolled_df_col, col_name, unit):
        new_col_name = (
            f"{col_name}_{StatsFeats.MIN.value}_{unit}_" f"{self.group_suffix}"
        )
        return new_col_name, rolled_df_col.min()

    def mean_features(self, rolled_df_col, col_name, unit):
        # AKA Simple Moving Average (SMA)
        new_col_name = (
            f"{col_name}_{StatsFeats.MEAN.value}_{unit}_" f"{self.group_suffix}"
        )
        return new_col_name, rolled_df_col.mean(numeric_only=True)

    def std_features(self, rolled_df_col, col_name, unit):
        new_col_name = (
            f"{col_name}_{StatsFeats.STD.value}_{unit}_" f"{self.group_suffix}"
        )

        if isinstance(rolled_df_col, pd.core.window.rolling.RollingGroupby):
            feature_value = rolled_df_col.apply(np.nanstd, engine=self.engine, raw=True)
        else:
            feature_value = rolled_df_col.std(ddof=0, numeric_only=True)

        return new_col_name, feature_value

    def median_features(self, rolled_df_col, col_name, unit):
        new_col_name = (
            f"{col_name}_{StatsFeats.MEDIAN.value}_" f"{unit}_{self.group_suffix}"
        )
        return new_col_name, rolled_df_col.median(numeric_only=True)

    def quantile_features(self, q=0.25):
        def apply_4q(rolled_df_col, col_name, unit):
            name = (
                StatsFeats.QUANTILE25.value
                if q == 0.25
                else StatsFeats.QUANTILE75.value
            )
            new_col_name = f"{col_name}_{name}_{unit}_{self.group_suffix}"

            if isinstance(rolled_df_col, pd.core.window.rolling.RollingGroupby):
                feature_value = rolled_df_col.quantile(quantile=q)
            else:
                feature_value = rolled_df_col.quantile(q=q)

            return new_col_name, feature_value

        return apply_4q

    def count_features(self, rolled_df_col, col_name, unit):
        new_col_name = (
            f"{col_name}_{StatsFeats.COUNT.value}_{unit}_" f"{self.group_suffix}"
        )
        return new_col_name, rolled_df_col.count()

    def build_features(self, df):
        """Add new columns to the initial Dataframe.

        Parameters
        ----------
        df : pandas.DataFrame
            The initial dataframe.

        Returns
        -------
        pandas.DataFrame
            The DataFrame with added features

        list of str
            Added columns names
        """

        self.df = df

        self._check_and_convert_date()
        self._check_required_columns()

        col_names = []

        # Sort dataframe by date to get right results for rolling operations
        self.df.sort_values(by=self.date_column, inplace=True)

        # Save the initial index and date to restore them after the changes
        # made while computing the advanced features
        self._index = self.df.index.tolist()
        self.initial_index_name = self.df.index.name
        self._date = self.df[self.date_column].tolist()

        # Keep only the date part and remove time information.
        self.df[self.date_column] = pd.to_datetime(self.df[self.date_column].dt.date)

        # Compute the advanced features
        for col in self.col_names:
            col_names.extend(self._all_features_4col(col))

        # Fill NaNs
        self.df[col_names] = self.df[col_names].astype("float32").fillna(0)

        # Restore initial index and date
        self.df["__index"] = self._index
        self.df.set_index("__index", inplace=True)
        self.df.index.name = self.initial_index_name
        self.df[self.date_column] = self._date

        return self.df, col_names

    def _check_and_convert_date(self):
        if self.date_column not in self.df.columns:
            raise ValueError(
                "DataFrame does not contain date " f"column {self.date_column}"
            )

        if self.df[self.date_column].dtype == np.object:
            try:
                self.df[self.date_column] = pd.to_datetime(self.df[self.date_column])
            except Exception as e:
                raise TypeError(
                    "Cannot convert date column "
                    f"{self.date_column} to datetime type."
                )

    def _check_required_columns(self):
        num_existing_columns = len(
            set(self.col_names).intersection(self.df.columns.tolist())
        )

        if num_existing_columns != len(self.col_names):
            raise ValueError(
                f"Couldn't find all columns: {self.col_names} " "in DataFrame"
            )

        for col in self.col_names:
            if not np.issubdtype(self.df[col].dtype, np.number):
                raise TypeError(
                    "Columns passed in col_names list must have "
                    f"numeric type. Column {col} doesn't have the "
                    "expected type."
                )

        if self.group_by not in self.df.columns.tolist():
            raise ValueError(
                f"Group_by column {self.group_by} cannot be " "found in DataFrame."
            )

    def _check_features(self, features):
        self.features = []

        for feat_name in features:
            if not StatsFeats.has_value(feat_name):
                logging.warning(f'Don\'t know how to implement "{feat_name}" feature.')
                continue

            self.features.append(feat_name)

    def _all_day_features_4col(self, group_df, col_name, windows):
        """Compute all features using day units for the specified column.
        """

        new_cols_names = []

        # Features computed on a given number of days
        for wind in windows:
            rolled_df_col = group_df[[col_name, self.date_column]].rolling(
                window=wind, on=self.date_column, closed="left"
            )

            # apply_all max, min, mean etc.
            for feat_name in self.features:
                # Compute rolled features
                new_col_name, rolled_feat_df = self._all_features[feat_name](
                    rolled_df_col, col_name, wind
                )
                new_cols_names.append(new_col_name)

                # Rename the column with the right value
                rolled_feat_df = rolled_feat_df.rename(
                    columns={col_name: new_col_name}
                ).reset_index(level=self.group_by)

                # Drop duplicated columns obtained for multiple samples with
                # the same date. The first values is the right one, while the
                # others contain information for the current day.
                rolled_feat_df = rolled_feat_df.drop_duplicates(
                    subset=[self.group_by, self.date_column], keep="first"
                ).fillna(0)

                # Merge the new feature to the dataset
                self.df = self.df.merge(
                    rolled_feat_df, on=[self.group_by, self.date_column], how="left"
                )

        return new_cols_names

    def _all_month_features_4col(self, group_df, col_name, windows):
        """Compute all features using month units on the speficied column.
        """

        feat_num = len(self.features)

        # Convert months from str to numerical type
        previous_months = _convert_units_to_integers(windows)

        # Find the interval in which to compute monthly features
        date_range = _compute_date_range(
            self.df, self.date_column, 2 * max(previous_months) + 1
        )

        # Generate names for new columns
        new_cols_names = self._generate_names_for_monthly_features(
            col_name, previous_months
        )
        all_month_features = pd.DataFrame(columns=new_cols_names, index=self.df.index)

        # Compute features for each group
        for _, group in tqdm(group_df):
            # Compute features for all months from date range
            monthly_features_df = self._compute_features_for_daterange(
                group, date_range, col_name
            )

            # Select the needed features for each sample from group
            for i, prev_month in enumerate(previous_months):
                group[prev_month] = group[self.date_column] + pd.offsets.MonthBegin(
                    n=-(prev_month + 1)
                )

                idx = group.index.tolist()
                cols = new_cols_names[i * feat_num : (i + 1) * feat_num]
                prev_months_date = group[prev_month].dt.date.values
                values = monthly_features_df.loc[prev_months_date].values

                all_month_features.loc[idx, cols] = values

        # Add features to the dataset
        self.df = self.df.merge(
            all_month_features.fillna(0).astype("float32"),
            left_index=True,
            right_index=True,
        )
        return new_cols_names

    def _generate_names_for_monthly_features(self, col_name, months):
        """Generate columns names for the speficied column and units.
        """

        new_cols_names = []

        for prev_month in months:
            for feat_name in self.features:
                new_col_name = (
                    f"{col_name}_{feat_name}_{prev_month}M_" f"{self.group_suffix}"
                )
                new_cols_names.append(new_col_name)

        return new_cols_names

    def _compute_features_for_daterange(self, group, date_range, col_name):
        """Compute all features for all months in date range.
        """

        monthly_features_df = pd.DataFrame(columns=self.features, index=date_range)
        month_bins = pd.cut(group[self.date_column], bins=date_range, right=False)

        for interval, month_group in group.groupby(month_bins):
            for feat_name in self.features:
                new_col_name, feat_value = self._all_features[feat_name](
                    month_group, col_name, f"{interval}"
                )

                monthly_features_df.loc[interval.left][feat_name] = feat_value[col_name]

        return monthly_features_df

    def _all_features_4col(self, col_name):
        """Compute all features for the specified column.
        """

        new_cols_names = []

        days_windows = [wind for wind in self.units if wind.find("M") == -1]
        months_windows = [wind for wind in self.units if wind.find("M") != -1]

        self.df[col_name] = self.df[col_name].astype("float64")

        # Compute advanced features on day unit
        if len(days_windows):
            group_df = self.df[[self.group_by, col_name, self.date_column]].groupby(
                self.group_by
            )

            new_cols_names += self._all_day_features_4col(
                group_df, col_name, days_windows
            )

        # Compute advanced features on month unit
        if len(months_windows):
            group_df = self.df[[self.group_by, col_name, self.date_column]].groupby(
                self.group_by
            )

            new_cols_names += self._all_month_features_4col(
                group_df, col_name, months_windows
            )

        return new_cols_names


def _convert_units_to_integers(units):
    """Extract the numerical value for a given unit.

        Parameters
        ----------
        units : list of str
            List of strings consisting from the number of units followed by
            the unit type: 'D' or 'M'.

        Returns
        -------
        list of int
            The numerical units
    """

    numeric_units = []

    # Convert units to integers
    for unit in units:
        try:
            numeric_units.append(int(unit[:-1]))
        except BaseException:
            logging.warning(f"Invalid unit format: {unit}")
            continue

    return numeric_units


def _compute_date_range(df, date_column, extra_months):
    """Compute the date range that includes all the samples from the dataset
        extended with a number of additional months.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataset.

        date_column : str
            The name of the date column.

        extra_months : int
            The number of additional months before the minimum date from the
            dataset to be included in date range.

        Returns
        -------
        pandas.date_range
            The date range.
    """

    min_date = df[date_column].dt.date.min() + pd.offsets.MonthBegin(
        n=-extra_months + 1
    )

    max_date = df[date_column].dt.date.max() + pd.offsets.MonthBegin(n=-1)

    months_num = int((max_date - min_date) / np.timedelta64(1, "M")) + 2
    date_range = pd.date_range(min_date, periods=months_num, freq="1MS")

    return date_range
