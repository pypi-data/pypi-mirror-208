import logging

from sklearn.base import BaseEstimator, TransformerMixin

from .graph_to_features import build_rwalk_features, graph_to_rwalk_features

# ---------------------------------------------------------------------------------
# list of existing random walk features
valid_rwalk_features = [
    "f_rwalk_start_amount",  # base features
    "f_rwalk_transfer_out",
    "f_rwalk_out_back",
    "f_rwalk_out_back_max",
    "f_rwalk_end_amount",
    "f_rwalk_transfer_in",
    "f_rwalk_in_back",
    "f_rwalk_in_back_max",
    "f_rwalk_ring_max",  # derivated features
    "f_rwalk_ring_average",
]


class RwalkFeatures(BaseEstimator, TransformerMixin):
    """Extract random walk features from graph.

    Given a graph whose nodes are clients' IDs and with edges attributes.

    * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
    * `'n_transactions'`: number of transactions between the two nodes
    compute random walk node features, as described in :ref:`sec-rwalk-features`.

    Parameters
    ----------
    rwalk_len: int, default=5
        Length of the random walk.

    rwalk_reps: int, default=100
        Number of random walks starting from the same node.

    prob_edge: string, default=None
        How to randomly choose the next node:
    
        * `None`: equal probabilities for all neighbors
        * `'cumulated_amount'`: probability is proportional with edge attribute 'cumulated_amount'
        * `'average_amount'`: probability is proportional with average amount (not yet implemented!!!)

    save_base_features: bool, default=False
        If True, random walk base features are computed only at first :meth:`transform` call.
        At further calls, only derivated features are computed, thus saving significant
        computation time. It is assumed that the graph is always the same, so it is
        user's responsibility to create a new class instance for a new graph.
        If False, the features are computed each time.

    precomputed_base_features: ndarray (number of nodes, number of base features), default=None
        Array of previously computed random walk base features.
        The number of base features is currently 8.
        Since the computation of the base features may take significant time,
        it is recommended to explicitly save the base features after a first :meth:`transform` call,
        then load them through this parameter for all subsequent uses.
        If *precomputed_base_features* is given, *save_base_features* is irrelevant.

    verbose : bool, default=False
        To control the verbosity of the procedure.

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
    
        from graphomaly.preprocessing.rwalk import RwalkFeatures
        my_list = ["f_rwalk_transfer_out", "f_rwalk_ring_max"]
        rw = RwalkFeatures(verbose=True)
        rw.fit(X, feature_list=my_list)
        Xf = rw.transform(X)

    The feature matrix Xf has 2 columns, corresponding to the features in my_list;
    each row corresponds to a node; nodes are sorted increasingly.
"""

    def __init__(
        self,
        rwalk_len=5,
        rwalk_reps=100,
        prob_edge=None,
        save_base_features=False,
        precomputed_base_features=None,
        verbose=False,
    ):
        self.rwalk_len = rwalk_len
        self.rwalk_reps = rwalk_reps
        self.prob_edge = prob_edge
        self.save_base_features = save_base_features
        self.verbose = verbose

        self.saved = False
        self.rwalk_base_features = None
        self.node_ids_ = None
        self.feature_names_in_ = None
        self.n_output_features_ = 0

        if precomputed_base_features is not None:
            self.rwalk_base_features = precomputed_base_features
            self.saved = True

    def fit(self, X, y=None, feature_list=None):
        """
        Validate and store feature_list to be computed by :meth:`transform`.
        Only valid feature names are retained.

        Parameters
        ----------
        feature_list : list of strings
            List of features names.
            If *None*, the base features will be computed.
        """

        if feature_list is not None:
            self.feature_names_in_ = feature_list.copy()

            for i in range(len(feature_list)):
                try:
                    valid_rwalk_features.index(feature_list[i])
                except ValueError:  # invalid feature
                    self.feature_names_in_.remove(feature_list[i])
                    logging.warning("Feature not found: %s", feature_list[i])

        return self

    def transform(self, X):
        """
        Compute node features using feature list stored and checked by :meth:`fit`.

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
            rwalk_features : ndarray (number of nodes, number of features)
                Array with node features.
        """

        # compute base features
        if not self.saved:
            self.rwalk_base_features, self.node_ids_ = graph_to_rwalk_features(
                X,
                self.rwalk_len,
                self.rwalk_reps,
                prob_edge=self.prob_edge,
                verbose=self.verbose,
            )
            if self.save_base_features:
                self.saved = True

        if self.feature_names_in_ is not None:
            rwalk_features = build_rwalk_features(
                self.feature_names_in_, self.rwalk_base_features
            )
        else:
            rwalk_features = self.rwalk_base_features

        self.n_output_features_ = rwalk_features.shape[1]

        return rwalk_features
