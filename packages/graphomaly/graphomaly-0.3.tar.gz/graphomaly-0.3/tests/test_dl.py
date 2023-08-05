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

from pyod.utils.data import generate_data
from sklearn.metrics import confusion_matrix

from graphomaly.models import ModelsLoader

CONTAMINATION = 0.1
N_TRAIN = 200  # number of training points
N_TEST = 100  # number of testing points

X, X_test, y, y_test = generate_data(
    n_train=N_TRAIN,
    n_test=N_TEST,
    n_features=2,
    contamination=CONTAMINATION,
    random_state=42,
    behaviour="new",
)

algorithm = "AnomalyDL"
clf = ModelsLoader.get(algorithm)
clf.fit(X)
y_pred = clf.predict(X_test)

tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
tpr = tp / (tp + fn)
tnr = tn / (tn + fp)
ba = (tpr + tnr) / 2
print(
    "BA: "
    + str(ba)
    + "   TPR: "
    + str(tpr)
    + "   TNR: "
    + str(tnr)
    + "   TN: "
    + str(tn)
    + "  FP: "
    + str(fp)
    + "   FN: "
    + str(fn)
    + "   TP:"
    + str(tp)
)
