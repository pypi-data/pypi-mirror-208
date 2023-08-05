# Copyright (c) 2021, 2022 Paul Irofti <paul@irofti.net>
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

from synthetic import SyntheticEstimator

type = "graph_to_features"
egonet_args = {
    "ctor_args": {
        "save_base_features": True,
        "verbose": True,
    },
    "fit_args": {
        "feature_list": [
            "f_degree_in",
            "f_degree_out",
            "f_amount_in",
            "f_amount_out",
            "f_nr_trans_in",
            "f_nr_trans_out",
            "f_ego_nr_nodes",
            "f_ego_nr_edges",
            "f_egored_degree_in",
            "f_egored_degree_out",
            "f_egored_amount_in",
            "f_egored_amount_out",
            "f_egored_nr_trans_in",
            "f_egored_nr_trans_out",
            "f_egored_nr_nodes",
            "f_egored_nr_edges",
            "f_average_amount_in",
            "f_average_amount_out",
            "f_egored_average_amount_in",
            "f_egored_average_amount_out",
            "f_egored_degree_in_rel",
            "f_egored_degree_out_rel",
            "f_egored_amount_in_rel",
            "f_egored_amount_out_rel",
            "f_egored_average_amount_in_rel",
            "f_egored_average_amount_out_rel",
            "f_egored_nr_nodes_rel",
            "f_egored_nr_edges_rel",
            "f_ego_edge_density",
            "f_egored_edge_density",
        ],
    },
}
rwalk_args = {
    "ctor_args": {
        "rwalk_len": 5,
        "rwalk_reps": 20,
        "save_base_features": True,
        "verbose": True,
    },
    "fit_args": {
        "feature_list": ["f_rwalk_transfer_out", "f_rwalk_ring_max"],
    },
}
spectrum_args = {
    "ctor_args": {"n_values": 2},
    "fit_args": {
        "feature_list": ["f_spectrum_Laplacian_amount"],
    },
}
to_feature_args = {
    "graph_algorithms": ["egonet", "rwalk", "spectrum"],
    "graph_algorithms_args": [egonet_args, rwalk_args, spectrum_args],
}
preprocessing_args = {
    "to_graph_args": {
        "summable_attributes": [3],
        "summable_attributes_out_names": ["nr_alerts"],
    },
    "to_features_args": to_feature_args,
}


clf = SyntheticEstimator(config_file="synthetic.yaml")

X, y, X_test, y_test = clf.load()

type = "graph_to_features"
_, _, _ = clf.preprocess(X, y, type, **to_feature_args)
_, _, _ = clf.preprocess(X_test, y_test, type, **to_feature_args)

type = "transactions_to_graph_to_features"
X, y, _ = clf.preprocess(X, y, type, **preprocessing_args)
clf.fit(X, y)

X_test, y_test, _ = clf.preprocess(X_test, y_test, type, **preprocessing_args)
y_test_pred = clf.predict(X_test)
