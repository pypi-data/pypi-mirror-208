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

import numpy as np
import logging


class DifferenceFeatures:
    """Compute difference features.

        Parameters
        ----------
        diff_columns : list of tuples of strings
            List of pairs of columns in DataFrame to compute differences on.
            The columns must have numeric type, otherwise an exception is
            raised.

        Attributes
        ----------
        name : str
            The name of the features computed by DifferenceFeatures class.

        Examples
        --------
        Given a toy dataframe:

        >>> df = pd.DataFrame({'amount': [100, 50, 30],
                               'date': ['2021-09-27', '2021-09-28', '2021-09-27'],
                               'userID': [1, 1, 2],
                               'amount_min_1D_userID': [0, 0, 100]
                              })
        >>> df
              amount	   date	    userID	amount_min_1D_userID
        0	100	    2021-09-27	1	    0
        1	50	    2021-09-28	1	    100
        2	30	    2021-09-27	2	    0

        To compute the difference between the current amount and the minimum
        amount from the previous day of each user, instantiate the class
        DifferenceFeatures as follows:

        >>> diffFeats = DifferenceFeatures([('amount', 'amount_min_1D_userID')])

        Compute difference features:

        >>> preprocessed_df, new_columns = diffFeats.build_features(df)

        The initial dataframe has a new column diff_amount_amount_min_1D_userID,
        containing the difference between the amount column and
        amount_min_1D_userID column:

        >>> preprocessed_df
              amount	date	   userID	amount_min_1D_userID	diff_amount_amount_min_1D_userID
        0	100	    2021-09-27	1	    0	                    100.0
        1	50	    2021-09-28	1	    100	                    -50.0
        2	30	    2021-09-27	2	    0	                    30.0

        The list of the new columns added through feature engineering is
        returned in new_columns variable:

        >>> new_columns
        ['diff_amount_amount_min_1D_userID']
    """

    def __init__(self, diff_columns):

        self.df = None
        self.diff_columns = diff_columns
        self.name = "DifferenceFeatures"

    def _check_columns(self, col1, col2):
        status_ok = True

        if col1 not in self.df.columns or col2 not in self.df.columns:
            logging.warning(
                "Couldn't find in DataFrame the columns from pair "
                f"({col1}, {col2}).Skipping this pair."
            )
            status_ok = False

        elif not np.issubdtype(self.df[col1].dtype, np.number) or not np.issubdtype(
            self.df[col1].dtype, np.number
        ):

            logging.warning(
                "Columns passed in diff_columns list must have "
                f"numeric type. Columns {col1} and {col2} do not "
                "have the expected type. Skipping them."
            )
            status_ok = False

        return status_ok

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
        col_names = []

        for col1, col2 in self.diff_columns:
            status_ok = self._check_columns(col1, col2)
            if not status_ok:
                continue

            new_col_name = f"diff_{col1}_{col2}"

            diff = self.df[col1].astype("float64") - self.df[col2].astype("float64")

            self.df[new_col_name] = diff.astype("float32")

            col_names.append(new_col_name)

        return self.df, col_names
