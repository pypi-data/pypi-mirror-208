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

from graphomaly import GraphomalyEstimator

config_file = None
models_train_all = False
models_subset = ["PyodIForest", "PyodLOF"]
models_ctor_kwargs = None
models_fit_kwargs = {
    "PyodIForest": {
        "n_estimators": [10, 30, 50],
        "bootstrap": [True, False],
        "contamination": [0.05, 0.1],
    },
    "PyodLOF": {
        "n_neighbors": [5, 10, 20],
        "algorithm": ["auto", "ball_tree", "brute"],
        "leaf_size": [15, 20, 30, 40],
        "metric": ["cityblock", "euclidean"],
        "contamination": [0.05, 0.1],
    },
}
n_cpus = 1
results_path = "results"
voting = "hard"
clf = GraphomalyEstimator(
    config_file=config_file,
    models_train_all=models_train_all,
    models_subset=models_subset,
    models_ctor_kwargs=models_ctor_kwargs,
    models_fit_kwargs=models_fit_kwargs,
    n_cpus=n_cpus,
    results_path=results_path,
    voting=voting,
)

assert clf.config_file == config_file
assert clf.models_train_all == models_train_all
assert clf.models_subset == models_subset
assert clf.models_ctor_kwargs == models_ctor_kwargs
assert clf.models_fit_kwargs == models_fit_kwargs
assert clf.n_cpus == n_cpus
assert clf.results_path == results_path
assert clf.voting == voting
