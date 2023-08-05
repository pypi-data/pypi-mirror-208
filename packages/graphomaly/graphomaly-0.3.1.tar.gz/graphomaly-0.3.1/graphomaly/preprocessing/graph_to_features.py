import logging
import random

import networkx as nx
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------------


def graph_to_egonet_features(
    G,
    FULL_egonets=True,
    IN_egonets=False,
    summable_attributes=[],
    labels=None,
    verbose=False,
):
    """Extract egonet features from input graph.

    Parameters
    ----------
    G : networkx DiGraph or pandas DataFrame or matrix
        Transactions graph. It must have the following edge attributes:

        * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
        * `'n_transactions'`: number of transactions between the two nodes

        It can have other attributes.
        A dataframe is immediately converted to Networkx graph, so there is no advantage in giving a dataframe.
        The columns for nodes forming an edge should be named `'id_source'` and `'id_destination'`.
        A matrix must have the following meanings for its first columns (in this order):
        id_source, id_destination, cumulated_amount, n_transactions.
        Further columns are disregarded. Each row represents an edge.

    FULL_egonets : bool, default=True
        Whether full undirected egonets (with radius 1) are considered.

    IN_egonets : bool, default=False
        Whether in or out egonets are considered, with respect to the current node.
        Is considered only if FULL_egonets=False.

    summable_attributes: list, default=[]
        List of edge attributes to be summed as adjacent nodes features.
        The name of the feature is the same as the name of the edge attribute.
        The attributes must be present in all edges; no check is made.
        If the input is a matrix, then summable_attributes must contain column numbers.

    labels : array, default=None
        Vector of transaction labels (0 is normal, >0 is abnormal).
        (An alternative way of giving the labels is to insert them in the graph
        as an edge attribute. The labels can be then processed through summable_attributes.)

    verbose : bool, default=False
        To control the verbosity of the procedure.

    Returns
    -------
    node_features : pandas dataframe (if input was graph or dataframe) or matrix (if input was matrix)
        Contains the following columns (in this order):

        * `'f_degree_in'`: in degree of the node
        * `'f_degree_out'`: out degree of the node
        * `'f_amount_in'`: total amount received by node from neighbors
        * `'f_amount_out'`: total amount sent by node to neighbors
        * `'f_nr_trans_in'`: number of transactions to the node
        * `'f_nr_trans_out'`: number of transactions from the node
        * `'f_ego_nr_nodes'`: number of nodes in the egonet
        * `'f_ego_nr_edges'`: number of edges in the egonet
        * `'f_egored_degree_in'`: from here below, the same features, but with respect to the reduced egonet
        * `'f_egored_degree_out'`
        * `'f_egored_amount_in'`
        * `'f_egored_amount_out'`
        * `'f_egored_nr_trans_in'`
        * `'f_egored_nr_trans_out'`
        * `'f_egored_nr_nodes'`
        * `'f_egored_nr_edges'`
        * other columns indicated by summable attributes

    node_ids : array
        Vector of node ids, sorted increasingly, corresponding to the rows of node_features.

    node_labels : array
        Vector of weighted node labels (0=normal, >0=the number of abnormal transactions
        in which that node is involved).
    """

    # BD 19.08.2021
    # BD 03.02.2022 revised to accept matrix input-output
    # BD 16.03.2022 labels may be given and transformed

    matrix_io = False
    Ns = len(summable_attributes)

    # add labels as edge attributes directly to graph, if graph input
    if isinstance(G, nx.DiGraph):
        if labels is not None:
            row = 0
            for e in G.edges:
                G[e[0]][e[1]]["_edge_labels_"] = labels[row]
                row += 1

    if isinstance(G, pd.DataFrame):  # if dataframe, convert to graph
        if labels is not None:  # append labels as column to dataframe
            G["_edge_labels_"] = labels
        G = nx.from_pandas_edgelist(
            df=G,
            source="id_source",
            target="id_destination",
            edge_attr=True,
            create_using=nx.DiGraph,
        )
    elif isinstance(G, np.ndarray):  # if matrix, convert to graph
        matrix_io = True
        # the easy way: convert first matrix to dataframe, then dataframe to graph
        if Ns == 0:  # if no other attributes, convert directly
            G = pd.DataFrame(
                G[:, 0:4],
                columns=[
                    "id_source",
                    "id_destination",
                    "cumulated_amount",
                    "n_transactions",
                ],
            )
        else:  # first copy attributes columns in another array
            Ga = np.copy(G[:, summable_attributes])
            G = pd.DataFrame(
                G[:, 0:4],
                columns=[
                    "id_source",
                    "id_destination",
                    "cumulated_amount",
                    "n_transactions",
                ],
            )
            for i in range(Ns):  # add columns for attributes
                G[str(summable_attributes[i])] = Ga[:, i]
                summable_attributes[i] = str(summable_attributes[i])
        if labels is not None:  # append labels as column to dataframe
            G["_edge_labels_"] = labels
        # convert dataframe to graph
        G = nx.from_pandas_edgelist(
            df=G,
            source="id_source",
            target="id_destination",
            edge_attr=True,
            create_using=nx.DiGraph,
        )
    elif not isinstance(G, nx.DiGraph):
        logging.error("Wrong data type for G")

    if not FULL_egonets and IN_egonets:  # reverse graph if in egonets are desired
        G = G.reverse(copy=False)

    if verbose:
        info = nx.info(G)
        print("Graph info:", info)

    # Build matrix of node features with the following columns (this is faster than using a dataframe)
    #  0 - degree in
    #  1 - degree out
    #  2 - amount in
    #  3 - amount out
    #  4 - number of transactions to node
    #  5 - number of transactions from node
    #  6 - egonet number of nodes
    #  7 - egonet nubber of edges
    #  8-15 - same as 0-7, but for reduced egonets (after removing nodes connected only with the center and only one-way)
    #  16-  - user specified summable attributes

    feat_ego_nr_nodes = 6
    feat_ego_nr_edges = 7
    feat_egored_nr_nodes = 14
    feat_egored_nr_edges = 15
    if not FULL_egonets and IN_egonets:  # in egonets, only where edge reversal matters
        feat_degree_in = 1
        feat_degree_out = 0
        feat_amount_in = 3
        feat_amount_out = 2
        feat_trans_nr_in = 5
        feat_trans_nr_out = 4
        feat_egored_degree_in = 9
        feat_egored_degree_out = 8
        feat_egored_amount_in = 11
        feat_egored_amount_out = 10
        feat_egored_trans_nr_in = 13
        feat_egored_trans_nr_out = 12
    else:  # full or out egonets
        feat_degree_in = 0
        feat_degree_out = 1
        feat_amount_in = 2
        feat_amount_out = 3
        feat_trans_nr_in = 4
        feat_trans_nr_out = 5
        feat_egored_degree_in = 8
        feat_egored_degree_out = 9
        feat_egored_amount_in = 10
        feat_egored_amount_out = 11
        feat_egored_trans_nr_in = 12
        feat_egored_trans_nr_out = 13

    Nn = G.number_of_nodes()
    Nef = 16  # number of egonet features
    Nf = (
        Nef + Ns
    )  # total number of features: egonets + number of user specified attributes

    # store features in matrix (it's faster)
    node_features = np.zeros((Nn, Nf))
    node_ids = np.zeros(Nn)
    if labels is not None:
        node_labels = np.zeros(Nn)
    else:
        node_labels = None

    # go over all nodes and extract features
    row = 0
    for node in G:
        # generate full egonet with ad hoc construction (networkx is slow!)
        if FULL_egonets:
            No = G.successors(node)
            Ni = G.predecessors(node)
            enodes = [node]  # create list of egonets nodes
            enodes.extend(No)
            enodes.extend(Ni)
            Gs = G.subgraph(enodes)
        else:  # out or in egonets
            Gs = nx.generators.ego.ego_graph(G, node, radius=1)

        node_ids[row] = node
        # in and out degree (that's easy) and total number of edges
        node_features[row, feat_degree_in] = Gs.in_degree(node)
        node_features[row, feat_degree_out] = Gs.out_degree(node)
        node_features[row, feat_ego_nr_nodes] = len(Gs)
        node_features[row, feat_ego_nr_edges] = Gs.to_undirected().number_of_edges()

        # Amounts in and out. Also, sums of user specified attributes
        amount_out = 0
        amount_in = 0
        trans_in = 0
        trans_out = 0
        s = np.zeros(Ns)
        for (
            e
        ) in (
            Gs.edges()
        ):  # go over edges and simply add amounts, transaction numbers, user specified attributes
            edge_data = Gs.get_edge_data(e[0], e[1])
            if e[0] == node:  # our node can be source
                amount_out += edge_data["cumulated_amount"]
                trans_out += edge_data["n_transactions"]
                for i in range(Ns):
                    s[i] += edge_data[summable_attributes[i]]
                if node_labels is not None:
                    node_labels[row] += edge_data["_edge_labels_"]
            if e[1] == node:  # or destination
                amount_in = amount_in + edge_data["cumulated_amount"]
                trans_in = trans_in + edge_data["n_transactions"]
                for i in range(Ns):
                    s[i] += edge_data[summable_attributes[i]]
                if node_labels is not None:
                    node_labels[row] += edge_data["_edge_labels_"]
        node_features[row, feat_amount_in] = amount_in
        node_features[row, feat_amount_out] = amount_out
        node_features[row, feat_trans_nr_in] = trans_in
        node_features[row, feat_trans_nr_out] = trans_out
        for i in range(Ns):
            node_features[row, Nef + i] = s[i]

        # Same operations on reduced egonets, which are obtained by removing lonely nodes from egonet
        # (a lonely node is connected only with a single edge to the central node of the egonet)
        enodes = []
        i_ego = 0
        for nn in Gs:
            if Gs.degree(nn) > 1:  # keep only nodes that have more than one neighbor
                enodes.append(nn)
                i_ego += 1

        # There is a case when egonet looks like this :
        #           degree: DiDegreeView({273172446621881.0: 3, 198112242249590.0: 1})
        #           edges: OutEdgeView([(273172446621881.0, 273172446621881.0), (198112242249590.0, 273172446621881.0)])
        #           in_edges: InEdgeView([(198112242249590.0, 273172446621881.0), (273172446621881.0, 273172446621881.0)])
        #           out_edges: OutEdgeView([(273172446621881.0, 273172446621881.0), (198112242249590.0, 273172446621881.0)])
        # And the current node is 198112242249590.0
        # As the degree of the current node is 1, it won't be added to the enodes list
        # This means that the reduced egonet doesn t contain the "ego" anymore
        # So the reduced egonet is empty
        if node not in enodes:
            i_ego = 0

        # if something left in the egonet (i.e., not a star)
        if i_ego > 0:
            Gs = Gs.subgraph(enodes[0:i_ego])  # the reduced egonet

            # Repeat the same operations as for the full egonet
            # In and out degree, total number of edges (they are smaller now, of course)
            node_features[row, feat_egored_degree_in] = Gs.in_degree(node)
            node_features[row, feat_egored_degree_out] = Gs.out_degree(node)
            node_features[row, feat_egored_nr_nodes] = len(Gs)
            node_features[
                row, feat_egored_nr_edges
            ] = Gs.to_undirected().number_of_edges()

            # Amounts in and out (they are also smaller and should be much smaller normally)
            amount_out = 0
            amount_in = 0
            trans_in = 0
            trans_out = 0
            for e in Gs.edges():  # go over edges and simply add amounts
                edge_data = Gs.get_edge_data(e[0], e[1])
                if e[0] == node:  # our node can be source
                    amount_out = amount_out + edge_data["cumulated_amount"]
                    trans_out = trans_out + edge_data["n_transactions"]
                if e[1] == node:  # or destination
                    amount_in = amount_in + edge_data["cumulated_amount"]
                    trans_in = trans_in + edge_data["n_transactions"]
            node_features[row, feat_egored_amount_in] = amount_in
            node_features[row, feat_egored_amount_out] = amount_out
            node_features[row, feat_egored_trans_nr_in] = trans_in
            node_features[row, feat_egored_trans_nr_out] = trans_out

        # that's all, go to next node
        row = row + 1
        if verbose:
            if row % 1000 == 0 or row == Nn:
                print("\r", "Nodes processed: ", row, end="\r", sep="", flush=True)

    if verbose:
        print("\r")

    # sort on id
    # node_features = node_features[np.argsort(node_features[:,0],0)]
    ii = np.argsort(node_ids)
    node_ids = node_ids[ii]
    node_features = node_features[ii]
    if node_labels is not None:
        node_labels = node_labels[ii]

    if not FULL_egonets and IN_egonets:
        G = G.reverse(copy=False)  # reverse back the graph, just in case

    if not matrix_io:  # convert matrix to dataframe
        df_columns = [
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
        ] + summable_attributes
        node_features = pd.DataFrame(node_features, columns=df_columns)

    return node_features, node_ids, node_labels


# ---------------------------------------------------------------------------------


def build_ego_features(
    feature_list,
    ego_base_features,
):
    """Build node egonet feature dataframe or matrix given the list of features
       and the base egonet features dataframe or matrix.

    Parameters
    ----------
    feature_list : list of strings
        List of features, each given by its Graphomaly name.
        The possible features are given in :ref:`sec-egonet-features`.

    ego_base_features : dataframe or matrix
        Precomputed feature values, stored in dataframe or matrix.

    Returns
    -------
    node_features : dataframe or matrix (same as in input)
        Values of the features.
    """
    # BD 9.02.2022

    base_feat_list = [
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
    ]

    matrix_io = False
    if isinstance(ego_base_features, np.ndarray):
        matrix_io = True
    else:  # it's dataframe, make matrix
        ego_base_features = ego_base_features.to_numpy()

    N = ego_base_features.shape[0]  # number of nodes
    node_features = np.zeros((N, len(feature_list)))

    f_good_list = (
        feature_list.copy()
    )  # working copy of the feature list, keeps the found features
    f_bad_list = []
    col_found = np.ones(len(feature_list))

    # compute features or just take them from the given base features
    for col in range(len(feature_list)):
        feat = feature_list[col]  # current feature
        try:
            i = base_feat_list.index(feat)  # if base feature, just copy
            node_features[:, col] = ego_base_features[:, i]
        except ValueError:  # not a base feature, must be computed
            if not compute_derivated_egonet_feature(
                ego_base_features, feat, node_features, col
            ):
                col_found[col] = 0  # feature not found
                f_good_list.remove(feat)
                f_bad_list.append(feat)

    if len(f_bad_list) > 0:
        logging.warning("Features not found: %s", f_bad_list)
        node_features = node_features[:, col_found != 0]

    if not matrix_io:  # make dataframe, if input was dataframe
        node_features = pd.DataFrame(node_features, columns=f_good_list)

    return node_features


# ---------------------------------------------------------------------------------


def compute_derivated_egonet_feature(
    ego_base_features,
    feature,
    node_features,
    col,
):
    """Build node feature dataframe given the list of features.

    Parameters
    ----------
    ego_base_features : matrix
        Base egonet features.

    feature : string
        The desired derivated feature name.

    node_features : matrix
        Matrix where to put the new feature values.

    col : int
        Column in the matrix where to put the new feature values.

    Returns
    -------
    feature_found: bool
        True if feature was found, false otherwise (corresponding column is zero in node_features).
    """
    # BD 9.02.2022

    action_dict = {
        "f_average_amount_in": ["div", 2, 4],  # "f_amount_in" / "f_nr_trans_in"
        "f_average_amount_out": [
            "div",
            3,
            5,
        ],  # "f_amount_out" / "f_nr_trans_out"
        "f_egored_average_amount_in": [
            "div",
            10,
            12,
        ],  # "f_egored_amount_in" / "f_egored_nr_trans_in"
        "f_egored_average_amount_out": [
            "div",
            11,
            13,
        ],  # "f_egored_amount_out" / "f_egored_nr_trans_out"
        "f_egored_degree_in_rel": ["div", 8, 0],  # "f_egored_degree_in" / "f_degree_in"
        "f_egored_degree_out_rel": [
            "div",
            9,
            1,
        ],  # "f_egored_degree_out" / "f_degree_out"
        "f_egored_amount_in_rel": [
            "div",
            10,
            2,
        ],  # "f_egored_amount_in" / "f_amount_in"
        "f_egored_amount_out_rel": [
            "div",
            11,
            3,
        ],  # "f_egored_amount_out" / "f_amount_out"
        "f_egored_average_amount_in_rel": [
            "div_rel",
            10,
            12,
            2,
            4,
        ],  # ("f_egored_amount_in"/"f_egored_nr_trans_in") / ("f_amount_in"/"f_nr_trans_in")
        "f_egored_average_amount_out_rel": [
            "div_rel",
            11,
            13,
            3,
            5,
        ],  # ("f_egored_amount_out"/"f_egored_nr_trans_out") / ("f_amount_out"/"f_nr_trans_out")
        "f_egored_nr_nodes_rel": [
            "div",
            14,
            6,
        ],  # "f_egored_nr_nodes" / "f_ego_nr_nodes"
        "f_egored_nr_edges_rel": [
            "div",
            15,
            7,
        ],  # "f_egored_nr_edges" / "f_ego_nr_edges"
        "f_ego_edge_density": ["div", 7, 6],  # "f_ego_nr_edges" / "f_ego_nr_nodes"
        "f_egored_edge_density": [
            "div",
            15,
            14,
        ],  # "f_egored_nr_edges" / "f_egored_nr_nodes"
    }

    try:
        op = action_dict[feature]  # feature found
    except:  # feature not found
        return False

    # compute the derivated feature
    if op[0] == "div":  # division of two base features
        mask = ego_base_features[:, op[2]] != 0
        if np.any(mask):
            node_features[mask, col] = (
                ego_base_features[mask, op[1]] / ego_base_features[mask, op[2]]
            )
    elif op[0] == "div_rel":  # division of two relative features
        mask = np.logical_and(
            ego_base_features[:, op[2]] != 0, ego_base_features[:, op[4]] != 0
        )
        mask = np.logical_and(mask, ego_base_features[:, op[3]] != 0)
        if np.any(mask):
            node_features[mask, col] = (
                ego_base_features[mask, op[1]] / ego_base_features[mask, op[2]]
            ) / (ego_base_features[mask, op[3]] / ego_base_features[mask, op[4]])

    return True


# ---------------------------------------------------------------------------------


def single_rwalk(
    G,
    node,
    rwalk_len,
    root_desc,
    out_walk=True,
    prob_edge=None,
):
    """Single random walk results.

    Parameters
    ----------
    G : networkx DiGraph
        Transactions graph. It must have the following edge attribute:

        * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node

    node : int
        Start node.

    rwalk_len : int
        The maximum length of the random walk.

    root_desc : vector of neighbor nodes
        If empty, it consists of all neighbors (successors or predecessors, depending on out_walk).

    out_walk : bool
        Direction of the random walk (True - from the node, False - to the node).

    prob_edge : string, default=None
        How to randomly choose the next node:

        * `None`: equal probabilities for all neighbors
        * `'cumulated_amount'`: probability is proportional with edge attribute `'cumulated_amount'`
        * `'average_amount'`: probability is proportional with average amount (not yet implemented!!!)

    Returns
    -------
    amount_start : real
        Amount on the first leg of the walk.

    amount_thru_walk : real
        Amount that goes through the whole walk, from start to finish (the minimum on all legs).

    amount_back : real
        Amount that comes back to the start node.

    """

    # BD 20.08.2021
    #    18.12.2021: added probability proportional with sum

    if len(root_desc) == 0:  # initialize neighbor list
        if out_walk:
            root_desc = np.asarray(list(G.successors(node)))
        else:
            root_desc = np.asarray(list(G.predecessors(node)))

    amount_thru_walk = np.inf  # minimum amount on the random walk (flow on that path)
    amount_back = 0  # amount that comes back to starting node
    desc = root_desc
    ndesc = root_desc.size
    crt_node = node
    for iw in range(rwalk_len):
        # add probabilities to edges if so required
        if prob_edge == None:  # equal probability between neighbors
            next_node = desc[random.randrange(ndesc)]
        else:  # for the moment we implement directly 'cumulated_amount'
            n_prob = np.zeros(ndesc)
            for ii in range(ndesc):
                if out_walk:
                    n_prob[ii] = G.get_edge_data(crt_node, desc[ii])["cumulated_amount"]
                else:
                    n_prob[ii] = G.get_edge_data(desc[ii], crt_node)["cumulated_amount"]
            n_prob = n_prob / np.sum(n_prob)  # normalize probabilities to 1
            next_node = np.random.choice(desc, p=n_prob)

        if out_walk:
            a = G.get_edge_data(crt_node, next_node)["cumulated_amount"]
        else:
            a = G.get_edge_data(next_node, crt_node)["cumulated_amount"]
        if iw == 0:  # amount on first hop of the random walk
            amount_start = a
        if a < amount_thru_walk:
            amount_thru_walk = (
                a  # amount that goes all the way to the end (it's the minimum)
            )
        if next_node == node:  # we are back in the starting node, money are back
            amount_back = amount_thru_walk
            break
        if (
            iw < rwalk_len - 1
        ):  # if not the last edge of the walk, prepare for next step
            crt_node = next_node
            if out_walk:
                desc = np.asarray(list(G.successors(crt_node)))
            else:
                desc = np.asarray(list(G.predecessors(crt_node)))
        ndesc = desc.size
        if ndesc == 0:  # we are in a sink
            break
    return amount_start, amount_thru_walk, amount_back


# ---------------------------------------------------------------------------------
def graph_to_rwalk_features(
    G,
    rwalk_len,
    rwalk_reps,
    prob_edge=None,
    verbose=False,
):
    """Extract random walk features from input graph.

    Parameters
    ----------
     G : networkx DiGraph or pandas DataFrame or matrix
        Transactions graph. It must have the following edge attributes:

        * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
        * `'n_transactions'`: number of transactions between the two nodes

        It can have other attributes.
        A dataframe is immediately converted to Networkx graph, so there is no advantage in giving a dataframe.
        The columns for nodes forming an edge should be named `'id_source'` and `'id_destination'`.
        A matrix must have the following meanings for its first columns (in this order):
        id_source, id_destination, cumulated_amount, n_transactions.
        Further columns are disregarded. Each row represents an edge.

    rwalk_len : int
        Length of the random walk.

    rwalk_reps : int
        Number of random walks starting from the same node.

    prob_edge : string, default=None
        How to randomly choose the next node:

        * `None`: equal probabilities for all neighbors
        * `'cumulated_amount'`: probability is proportional with edge attribute 'cumulated_amount'
        * `'average_amount'`: probability is proportional with average amount (not yet implemented!!!)

    verbose : bool, default=False
        To control the verbosity of the procedure.

    Returns
    -------
    node_features : pandas dataframe (if input was graph or dataframe) or matrix (if input was matrix)
        Contains the following columns (in this order):

        * `'f_rwalk_start_amount'`: average amount on the first leg of the random walk (starting from the node)
        * `'f_rwalk_transfer_out'`: average amount going through the whole walk (the minimum over all legs)
        * `'f_rwalk_out_back'`: average amount coming back to the node
        * `'f_rwalk_out_back_max'`: maximum amount coming back to the node ("best ring")
        * `'f_rwalk_end_amount'`: same as above, but for random walks finishing in the node
        * `'f_rwalk_transfer_in'`
        * `'f_rwalk_in_back'`
        * `'f_rwalk_in_back_max'`

    node_ids : vector
        Contains node ids, sorted increasingly, corresponding to the rows of node_features.

    """
    # BD 20.08.2021
    #    18.12.2021 added probability proportional with sum
    #    13.02.2022 revised to accept matrix input-output

    matrix_io = False

    if isinstance(G, pd.DataFrame):  # if dataframe, convert to graph
        G = nx.from_pandas_edgelist(
            df=G,
            source="id_source",
            target="id_destination",
            edge_attr=True,
            create_using=nx.DiGraph,
        )
    elif isinstance(G, np.ndarray):  # if matrix, convert to graph
        matrix_io = True
        # the easy way: convert first matrix to dataframe, then dataframe to graph
        G = pd.DataFrame(
            G[:, 0:4],
            columns=[
                "id_source",
                "id_destination",
                "cumulated_amount",
                "n_transactions",
            ],
        )
        G = nx.from_pandas_edgelist(
            df=G,
            source="id_source",
            target="id_destination",
            edge_attr=True,
            create_using=nx.DiGraph,
        )
    else:
        logging.warning("Wrong data type for G")

    N = G.number_of_nodes()
    node_features = np.zeros((N, 8))  # matrix for storing random walk features
    node_ids = np.zeros(N)
    inode = 0
    for node in G:
        node_ids[inode] = node
        root_desc = np.asarray(list(G.successors(node)))  # vector of neighbors
        if root_desc.size > 0:  # if the node has no successors, there is nothing to do
            rwalk_start_amounts = np.zeros(rwalk_reps)
            rwalk_thru_amounts = np.zeros(rwalk_reps)
            rwalk_back_amounts = np.zeros(rwalk_reps)

            # generate the random walks - starting from the node
            for ir in range(rwalk_reps):
                (
                    rwalk_start_amounts[ir],
                    rwalk_thru_amounts[ir],
                    rwalk_back_amounts[ir],
                ) = single_rwalk(G, node, rwalk_len, root_desc, True, prob_edge)

            node_features[inode, 0] = np.average(rwalk_start_amounts)
            node_features[inode, 1] = np.average(rwalk_thru_amounts)
            node_features[inode, 2] = np.average(rwalk_back_amounts)
            node_features[inode, 3] = np.max(rwalk_back_amounts)

        # same operations, backward from the starting node (==> walks finishing in the node)
        root_desc = np.asarray(
            list(G.predecessors(node))
        )  # we keep the same variables, but the meaning is different
        if (
            root_desc.size > 0
        ):  # if the node has no predecessors, there is nothing to do
            rwalk_start_amounts = np.zeros(rwalk_reps)
            rwalk_thru_amounts = np.zeros(rwalk_reps)
            rwalk_back_amounts = np.zeros(rwalk_reps)

            for ir in range(rwalk_reps):
                (
                    rwalk_start_amounts[ir],
                    rwalk_thru_amounts[ir],
                    rwalk_back_amounts[ir],
                ) = single_rwalk(G, node, rwalk_len, root_desc, False, prob_edge)

            node_features[inode, 4] = np.average(rwalk_start_amounts)
            node_features[inode, 5] = np.average(rwalk_thru_amounts)
            node_features[inode, 6] = np.average(rwalk_back_amounts)
            node_features[inode, 7] = np.max(rwalk_back_amounts)

        inode += 1
        if verbose:
            if inode % 1000 == 0 or inode == N:
                print("\r", "Nodes processed: ", inode, end="\r", sep="", flush=True)

    if verbose:
        print("\r")

    # sort on id
    ii = np.argsort(node_ids)
    node_ids = node_ids[ii]
    node_features = node_features[ii]

    if not matrix_io:  # convert matrix to dataframe
        df_columns = [
            "f_rwalk_start_amount",
            "f_rwalk_transfer_out",
            "f_rwalk_out_back",
            "f_rwalk_out_back_max",
            "f_rwalk_end_amount",
            "f_rwalk_transfer_in",
            "f_rwalk_in_back",
            "f_rwalk_in_back_max",
        ]
        node_features = pd.DataFrame(node_features, columns=df_columns)

    return node_features, node_ids


# ---------------------------------------------------------------------------------


def build_rwalk_features(feature_list, rwalk_base_features):
    """Build node random walk feature dataframe or matrix given the list of features
       and the base egonet features dataframe or matrix.

    Parameters
    ----------
    feature_list : list of strings
        List of features, each given by its Graphomaly name.
        The possible features are given in :ref:`sec-rwalk-features`.

    rwalk_base_features : dataframe or matrix
        Precomputed feature values, stored in dataframe or matrix.

    Returns
    -------
    node_features : dataframe or matrix (same as in input)
        Values of the features.
    """
    # BD 13.02.2022

    base_feat_list = [
        "f_rwalk_start_amount",
        "f_rwalk_transfer_out",
        "f_rwalk_out_back",
        "f_rwalk_out_back_max",
        "f_rwalk_end_amount",
        "f_rwalk_transfer_in",
        "f_rwalk_in_back",
        "f_rwalk_in_back_max",
    ]

    matrix_io = False
    if isinstance(rwalk_base_features, np.ndarray):
        matrix_io = True
    else:  # it's dataframe, make matrix
        rwalk_base_features = rwalk_base_features.to_numpy()

    N = rwalk_base_features.shape[0]  # number of nodes
    node_features = np.zeros((N, len(feature_list)))

    f_good_list = (
        feature_list.copy()
    )  # working copy of the feature list, keeps the found features
    f_bad_list = []
    col_found = np.ones(len(feature_list))

    # compute features or just take them from the given base features
    for col in range(len(feature_list)):
        feat = feature_list[col]  # current feature
        try:
            i = base_feat_list.index(feat)  # if base feature, just copy
            node_features[:, col] = rwalk_base_features[:, i]
        except ValueError:  # not a base feature, must be computed
            if feat == "f_rwalk_ring_max":
                node_features[:, col] = np.maximum(
                    rwalk_base_features[:, 3], rwalk_base_features[:, 7]
                )
            elif feat == "f_rwalk_ring_average":
                node_features[:, col] = (
                    rwalk_base_features[:, 3] + rwalk_base_features[:, 7]
                ) / 2
            else:  # feature not found
                col_found[col] = 0
                f_good_list.remove(feat)
                f_bad_list.append(feat)

    if len(f_bad_list) > 0:
        logging.warning("Features not found: %s", f_bad_list)
        node_features = node_features[:, col_found != 0]

    if not matrix_io:  # make dataframe, if input was dataframe
        node_features = pd.DataFrame(node_features, columns=f_good_list)

    return node_features


# ---------------------------------------------------------------------------------
