import logging

from sklearn.base import BaseEstimator, TransformerMixin

from .graph_to_features import build_ego_features, graph_to_egonet_features

# ---------------------------------------------------------------------------------
# list of existing egonet features
valid_egonet_features = [
    "f_degree_in",  # base features
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
    "f_average_amount_in",  # derivated features
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
]


class EgonetFeatures(BaseEstimator, TransformerMixin):
    """Extract egonet features from graph.

    Given a graph whose nodes are clients IDs and with edges attributes

    * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
    * `'n_transactions'`: number of transactions between the two nodes
    compute node features, as described in :ref:`sec-egonet-features`.

    Parameters
    ----------
    FULL_egonets : bool, default=True
        Whether full undirected egonets (with radius 1) are considered.

    IN_egonets : bool, default=False
        Whether in or out egonets are considered, with respect to the current node.
        Is considered only if FULL_egonets=False.

    save_base_features: bool, default=False
        If True, egonet base features are computed only at first :meth:`transform` call.
        At further calls, only derivated features are computed, thus saving significant
        computation time. It is assumed that the graph is always the same, so it is
        user's responsibility to create a new class instance for a new graph.
        If False, the features are computed each time.
        
    precomputed_base_features: ndarray (number of nodes, number of base features), default=None
        Array of previously computed egonet base features.
        The number of base features is currently 16.
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
        
    labels_ : array
        Vector of node labels (0=normal, 1=abnormal).
        
    labels_weighted_ : array
        Vector of weighted node labels (0=normal, >0=the number of abnormal transactions
        in which that node is involved).

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
    
        from graphomaly.preprocessing.egonet import EgonetFeatures
        my_list = ["f_degree_in", "f_ego_edge_density", "f_egored_edge_density",
                   "f_amount_in", "f_egored_amount_in"]
        ego = EgonetFeatures()
        ego.fit(X, feature_list=my_list)
        Xf = ego.transform(X)

    The feature matrix Xf has 5 columns, corresponding to the features in my_list;
    each row corresponds to a node; nodes are sorted increasingly.
    """

    def __init__(
        self,
        FULL_egonets=True,
        IN_egonets=False,
        save_base_features=False,
        precomputed_base_features=None,
        verbose=False,
    ):
        self.FULL_egonets = FULL_egonets
        self.IN_egonets = IN_egonets
        self.save_base_features = save_base_features
        self.verbose = verbose

        self.saved = False
        self.ego_base_features = None
        self.node_ids_ = None
        self.feature_names_in_ = None
        self.n_output_features_ = 0
        
        self.y_saved = None
        self.labels_ = None
        self.labels_weighted_ = None
        
        if precomputed_base_features is not None:
            self.ego_base_features = precomputed_base_features
            self.saved = True

    def fit(self, X, y=None, feature_list=None):
        """
        Validate and store feature_list to be computed by :meth:`transform`.
        Only valid feature names are retained.

        Parameters
        ----------
        X : networkx DiGraph or pandas DataFrame or matrix
            Transactions graph. See :meth:`transform` for details.
            
        y : array
            Vector of transaction labels (0 is normal, >0 is abnormal).
            An entry with value *n* means that *n* transactions between the two
            nodes are abnormal. The usual interpretation 0=normal, 1=abnormal
            is a particular case.

        feature_list : list of strings
            List of features names.
            If *None*, the base features will be computed.
        """

        if feature_list is not None:
            self.feature_names_in_ = feature_list.copy()

            for i in range(len(feature_list)):
                try:
                    valid_egonet_features.index(feature_list[i])
                except ValueError:  # invalid feature
                    self.feature_names_in_.remove(feature_list[i])
                    logging.warning("Feature not found: %s", feature_list[i])
                    
        if y is not None:
            self.y_saved = y

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
            ego_features : ndarray (number of nodes, number of features)
                Array with node features.
        """

        # compute base features, if necessary
        if not self.saved:
            self.ego_base_features, self.node_ids_, self.labels_weighted_ = graph_to_egonet_features(
                X,
                FULL_egonets=self.FULL_egonets,
                IN_egonets=self.IN_egonets,
                labels=self.y_saved,
                verbose=self.verbose,
            )
            if self.save_base_features:
                self.saved = True
            if self.labels_weighted_ is not None:
                self.labels_ = (self.labels_weighted_ != 0).astype(int)

        if self.feature_names_in_ is not None:
            ego_features = build_ego_features(
                self.feature_names_in_, self.ego_base_features
            )
        else:
            ego_features = self.ego_base_features

        self.n_output_features_ = ego_features.shape[1]

        return ego_features
