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
import logging

from enum import Enum


class TimeFeats(Enum):
    DAY_OF_YEAR = 'day_of_year'
    DAY_OF_MONTH = 'day_of_month'
    DAY_OF_WEEK = 'day_of_week'
    YEAR = 'year'
    MONTH = 'month'
    WEEK = 'week'
    HOUR = 'hour'
    MINUTES_OF_HOUR = 'minutes_of_hour'
    MINUTES_OF_DAY = 'minutes_of_day'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


ALL_TIME_FEATS = list(map(lambda x: x.value, TimeFeats))


class TimeFeatures():
    """Compute time features.

        Parameters
        ----------
        date_column : str
            The column containing the date, in numpy.datetime64 format.

        features : list of str, default=['day_of_year', 'day_of_month', 'day_of_week', 'year', 'month', 'week', 'hour', 'minutes_of_hour', 'minutes_of_day']
            List of time features to be computed. Available options are:

            - 'day_of_year': the number of the day in the year specified by date.
            - 'day_of_month': the number of the day in the month specified by date.
            - 'day_of_week': the number of the day in the week specified by date.
            - 'year': the year specified by date.
            - 'month': the month specified by date.
            - 'hour': the hour specified by date.
            - 'minutes_of_hour': the minutes specified by date.
            - 'minutes_of_day': the hour and minutes converted to minutes.

        Attributes
        ----------
        name : str
            The name of the features computed by TimeFeatures class.

        Examples
        --------
        Given a toy dataframe:

        >>> df = pd.DataFrame({'amount': [100, 50, 30],
                               'date': ['2021-09-27', '2021-09-28', '2021-09-27'],
                               'userID': [1, 1, 2]
                              })
        >>> df
              amount          date    userID
        0	100	    2021-09-27	1
        1	50	    2021-09-28	1
        2	30	    2021-09-27	2

        To extract the number of the day in the month, the year and the month
        for each sample in the dataframe, instantiate the class TimeFeatures
        as follows:

        >>> timeFeats = TimeFeatures('date',
                                     features=['day_of_month', 'year', 'month'])

        Compute time features:

        >>> preprocessed_df, new_columns = timeFeats.build_features(df)

        The initial dataframe has 3 new columns corresponding to the time
        features:

        >>> preprocessed_df
              amount          date   userID   day_of_month        year       month
        0	100	    2021-09-27	1	    27	            2021	9
        1	50	    2021-09-28	1	    28	            2021	9
        2	30	    2021-09-27	2	    27	            2021	9

        The list of the new columns added through feature engineering is
        returned in new_columns variable

        >>> new_columns
        ['day_of_month', 'year', 'month']
    """

    def __init__(self, date_column, features=ALL_TIME_FEATS):
        self.df = None
        self.date_column = date_column
        self.features = features
        self.name = 'TimeFeatures'

        self._all_features = {
            TimeFeats.DAY_OF_YEAR.value: self.day_of_year,
            TimeFeats.DAY_OF_MONTH.value: self.day_of_month,
            TimeFeats.DAY_OF_WEEK.value: self.day_of_week,
            TimeFeats.YEAR.value: self.year,
            TimeFeats.MONTH.value: self.month,
            TimeFeats.WEEK.value: self.week,
            TimeFeats.HOUR.value: self.hour,
            TimeFeats.MINUTES_OF_HOUR.value: self.minutes_of_hour,
            TimeFeats.MINUTES_OF_DAY.value: self.minutes_of_day,
        }

    def day_of_year(self):
        new_col_name = "day_of_year"
        self.df[new_col_name] = self.df[self.date_column].dt.dayofyear

        return new_col_name

    def day_of_month(self):
        new_col_name = "day_of_month"
        self.df[new_col_name] = self.df[self.date_column].dt.day

        return new_col_name

    def day_of_week(self):
        new_col_name = "day_of_week"
        self.df[new_col_name] = self.df[self.date_column].dt.dayofweek

        return new_col_name

    def year(self):
        new_col_name = "year"
        self.df[new_col_name] = self.df[self.date_column].dt.year

        return new_col_name

    def month(self):
        new_col_name = "month"
        self.df[new_col_name] = self.df[self.date_column].dt.month

        return new_col_name

    def week(self):
        new_col_name = "week"
        self.df[new_col_name] = self.df[self.date_column].dt.isocalendar() \
                                    .week.astype('int64')

        return new_col_name

    def hour(self):
        new_col_name = "hour"
        self.df[new_col_name] = self.df[self.date_column].dt.hour

        return new_col_name

    def minutes_of_hour(self):
        new_col_name = "minutes_of_hour"
        self.df[new_col_name] = self.df[self.date_column].dt.minute

        return new_col_name

    def minutes_of_day(self):
        new_col_name = "minutes_of_day"
        self.df[new_col_name] = self.df[self.date_column].dt.hour * 60 + \
            self.df[self.date_column].dt.minute

        return new_col_name

    def build_features(self, df):
        """Add new columns to the initial Dataframe, according to the list of features
            given to the constructor.

            Parameters
            ----------
            df : pandas.DataFrame
                The initial dataframe.

            Returns
            -------
            list of str
                List with added columns names
        """

        self.df = df
        self._check_and_convert_date()

        new_cols_names = []

        for feat_name in self.features:
            if not TimeFeats.has_value(feat_name):
                logging.warning(
                    "Don't know how to implement \"{}\" feature.".
                    format(feat_name))
                continue

            col_name = self._all_features[feat_name]()
            new_cols_names.append(col_name)

        return self.df, new_cols_names

    def _check_and_convert_date(self):
        if self.date_column not in self.df.columns:
            raise ValueError("DataFrame does not contain date "
                             f"column {self.date_column}")

        if self.df[self.date_column].dtype == np.object:
            try:
                self.df[self.date_column] = \
                    pd.to_datetime(self.df[self.date_column])
            except Exception as e:
                raise TypeError("Cannot convert date column "
                                f"{self.date_column} to datetime type.")


class GroupHistoricalTimeFeatures():
    """Compute historical time features.

        Parameters
        ----------
        date_column : str
            The column containing the date in numpy.datetime64 format.

        group_by : str
            The column to group by.

        units : list of str, default=['h', 'm']
            The units in which to compute the differences. Available units:
            'h' (hour), 's' (second), 'm' (minute), 'D' (day)

        group_suffix : str, default=''
            A suffix to be appended to the resulting columns in order to
            differentiate between the same features computed for different
            group ids.

        Attributes
        ----------
        name : str
            The name of the features computed by GroupHistoricalTimeFeatures
            class.

        all_units : list of str
            The list of available units.

        Examples
        --------
        Given a toy dataframe:

        >>> df = pd.DataFrame({'amount': [100, 50, 30],
                               'date': ['2021-09-27', '2021-09-28', '2021-09-27'],
                               'userID': [1, 1, 2]
                              })
        >>> df
                amount	    date	userID
        0	100	    2021-09-27	1
        1	50	    2021-09-28	1
        2	30	    2021-09-27	2

        To compute the difference in hour and minutes between the current sample
        and the previous sample (sorted in ascending order by date) for each
        userID in the dataframe, instantiate class GroupHistoricalTimeFeatures
        as follows:

        >>> histFeats = GroupHistoricalTimeFeatures('date',
                                                    group_by='userID',
                                                    units=['h', 'm'])

        Compute the historical time features:

        >>> preprocessed_df, new_columns = histFeats.build_features(df)

        The initial dataframe 2 new columns 'date_diff_h_userID' and
        'date_diff_m_userID' containing the differences between consecutive
        samples (computed on date column after sorting it in ascending order),
        reported in hours (h) and minutes (m), for each user for userID column
        from the dataset:

        >>> preprocessed_df
            amount	date	    userID	date_diff_h_userID	date_diff_m_userID
        0	100	    2021-09-27	1	    -1.0	            -1.0
        1	50	    2021-09-28	1	    24.0	            1440.0
        2	30	    2021-09-27	2	    -1.0	            -1.0

        The list of the new columns added through feature engineering is
        returned in new_columns variable.

        >>> new_columns
        ['date_diff_h_userID', 'date_diff_m_userID']
    """

    def __init__(
            self,
            date_column,
            group_by,
            units=['h', 'm'],
            group_suffix=''):

        self.df = None
        self.date_column = date_column
        self.group_by = group_by
        self.units = units
        self.group_suffix = group_suffix if group_suffix != '' \
            else str(group_by)[:8]

        self.all_units = ['h', 'm', 's', 'D']
        self.name = f"GroupHistTimeFeatures_{self.group_suffix}"

    def build_features(self, df):
        """Add new columns to the initial Dataframe.

            Parameters
            ----------
            df : pandas.DataFrame
                The initial dataframe.

            Returns
            -------
            list of str
                Added columns names
        """

        self.df = df
        self._check_and_convert_date()
        self._check_params()

        col_names = []

        timedelta = self.df.sort_values(by=self.date_column) \
                           .groupby(by=self.group_by)[self.date_column] \
                           .diff(periods=1)

        for unit in self.units:
            new_col_name = f"{self.date_column}_diff_{unit}_{self.group_suffix}"
            self.df[new_col_name] = (timedelta / np.timedelta64(1, unit))\
                .astype('float32')
            col_names.append(new_col_name)

        self.df[col_names] = self.df[col_names].fillna(-1)

        return self.df, col_names

    def _check_and_convert_date(self):
        if self.date_column not in self.df.columns:
            raise ValueError("DataFrame does not contain date "
                             f"column {self.date_column}")

        if self.df[self.date_column].dtype == np.object:
            try:
                self.df[self.date_column] = pd.to_datetime(
                    self.df[self.date_column])
            except Exception as e:
                raise TypeError(
                    f"Cannot convert date column {self.date_column} "
                    "to datetime type.")

    def _check_params(self):
        if self.group_by not in self.df.columns.tolist():
            raise ValueError(f"Group_by column {self.group_by} cannot be "
                             "found in DataFrame.")

        unknown_units = set(self.units) - set(self.all_units)
        if len(unknown_units):
            raise ValueError(f"Unknown units: {unknown_units}.")
