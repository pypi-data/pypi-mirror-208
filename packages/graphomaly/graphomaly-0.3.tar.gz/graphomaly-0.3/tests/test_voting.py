# Copyright (c) 2022 Andra Băltoiu <andra.baltoiu@gmail.com>
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

from graphomaly.models import ModelsLoader
from graphomaly.voting import VotingClassifier

CONTAMINATION = 0.1

n_estimators = 3
voting = "hard"
estimators = []
clf = []

for i, algorithm in enumerate(ModelsLoader.models):
    clf = ModelsLoader.get(algorithm)
    estimators.append((algorithm, clf))
    if i > n_estimators:
        break

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

eclf = VotingClassifier(estimators=estimators, voting=voting)
eclf.fit(X)
y_test_pred = eclf.predict(X_test)
