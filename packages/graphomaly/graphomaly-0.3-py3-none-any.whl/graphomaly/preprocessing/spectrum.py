# Copyright (c) 2022 Andrei Pătrașcu <andrei.patrascu@fmi.unibuc.ro>
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

from sklearn.base import BaseEstimator, TransformerMixin

import logging

from .graph_to_spectrum_features import graph_to_spectrum_features

# list of implemented spectrum egonet features
valid_egonet_spectrum_features = [
    "f_spectrum_Laplacian",
    "f_spectrum_Laplacian_amount",
    "f_spectrum_Laplacian_average_amount",
    "f_spectrum_Laplacian_n_transactions",
]

class SpectrumFeatures(BaseEstimator, TransformerMixin):
    """Extract egonet spectrum features from graph [1]_

    Given a graph whose nodes are clients IDs and with edges attributes

    * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
    * `'n_transactions'`: number of transactions between the two nodes

    compute node features, as described in :ref:`sec-egonet-spectrum-features`.

    Parameters
    ----------
    FULL_egonets : bool, default=True
        Whether full undirected egonets (with radius 1) are considered

    IN_egonets : bool, default=False
        Whether in or out egonets are considered, with respect to the current node.
        Is considered only if FULL_egonets=False.

    n_values : int, default=5
        Number of largest singular values to be computed.

    Attributes
    ----------
    node_ids_ : array
        Vector of node IDs, sorted increasingly.
        It can be seen as the integer labels associated with the final node feature matrix,
        which is sorted accordingly.

    feature_names_in_ : list of strings
        List of valid features extracted from user given feature list in :meth:`fit`.

    n_output_features_ : int
        Number of computed features (number of columns of node feature matrix).

    Example
    -------
    Assume X is a matrix describing a graph, each row representing an edge.
    The first four columns are: id_source, id_destination, cumulated_amount, n_transactions.
    The following code computes a few features.

    .. code-block:: python
    
        from graphomaly.preprocessing.spectrum import SpectrumFeatures
        my_list = ["f_spectrum_Laplacian_amount"]
        sp = SpectrumFeatures(n_values=3)
        sp.fit(X, feature_list=my_list)
        Xf = sp.transform(X)

    The feature matrix Xf has 3 columns: we have a feature in my_list and
    indicated that we want to compute n_values=3 singular values;
    each row corresponds to a node; nodes are sorted increasingly.

    References
    ----------
    .. [1] Huang, S., et al., Laplacian change point detection for dynamic
        graphs, Proceedings of the 26th ACM SIGKDD International Conference on
        Knowledge Discovery & Data Mining, 2020.
        https://doi.org/10.1145/3394486.3403077
    """

    def __init__(
        self,
        FULL_egonets=True,
        IN_egonets=False,
        n_values=5,
    ):
        self.FULL_egonets = FULL_egonets
        self.IN_egonets = IN_egonets

        self.ego_spectrum_features = None
        self.node_ids_ = None
        self.spectrum_feature_list = None
        self.feature_names_in_ = None
        self.n_output_features_ = 0
        self.n_values = n_values

    def fit(self, X, y=None, feature_list=None):
        """
        Validate and store feature_list to be computed by :meth:`transform`.
        Only valid feature names are retained.

        Parameters
        ----------
        X : networkx DiGraph or pandas DataFrame or matrix
            Transactions graph. See :meth:`transform` for details.
            
        y : array
            Not used. Here only for compatibility reasons.

        feature_list : list of strings
            List of features names.
            If *None*, no feature will be computed.
        """
        if feature_list is not None:
            self.spectrum_feature_list = feature_list.copy()

            for i in range(len(feature_list)):
                try:
                    valid_egonet_spectrum_features.index(feature_list[i])
                except ValueError:  # invalid feature
                    self.spectrum_feature_list.remove(feature_list[i])
                    logging.warning("Feature not found: %s", feature_list[i])

            self.feature_names_in_ = []
            for feat in self.spectrum_feature_list:
                for i in range(1, self.n_values+1):
                    self.feature_names_in_.append(feat + "_" + str(i))
                    
        return self

    def transform(self, X):
        """
        Compute node spectrum features.

        Parameters
        ----------
        X : networkx DiGraph or pandas DataFrame or matrix
            Transactions graph. It must have the following edge attributes:

            * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
            * `'n_transactions'`: number of transactions between the two nodes

            It can have other attributes.
            A dataframe is immediately converted to Networkx graph, so there is no advantage in giving a dataframe.
            The columns for nodes forming an edge should be named `'id_source'` and `'id_destination'`.
            A matrix must have the following meanings for its first columns (in this order):
            id_source, id_destination, cumulated_amount, n_transactions.
            Further columns are disregarded. Each row represents an edge.

        Returns
        -------
            ego_spectrum_features : ndarray (number of nodes, number of features)
                Array with node features.
        """

        if self.spectrum_feature_list is None:
            return None
        else:
            self.ego_spectrum_features, self.node_ids_ = graph_to_spectrum_features(
                X,
                FULL_egonets=self.FULL_egonets,
                IN_egonets=self.IN_egonets,
                feature_list=self.spectrum_feature_list,
                n_values=self.n_values,
            )
            self.n_output_features_ = self.ego_spectrum_features.shape[1]

            return self.ego_spectrum_features
