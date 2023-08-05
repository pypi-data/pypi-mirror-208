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

import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer

from graphomaly.preprocessing.fe_time_transformers import TimeFeatTransformer

the_bread_basket = fetch_openml("The-Bread-Basket", as_frame=True)
df = the_bread_basket.frame

# Create a column transformer
# Replace the date_time column with its corresponding features and
# pass_through all the others.
column_trans = ColumnTransformer(
    [("time_feats_tr", TimeFeatTransformer(), ["date_time"])], remainder="passthrough"
)

X_r = column_trans.fit_transform(df)
df_out = pd.DataFrame(X_r, columns=column_trans.get_feature_names_out())

print(df_out.head())
