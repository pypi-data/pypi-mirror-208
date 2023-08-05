# Copyright (c) 2022 Andrei Pătrașcu <andrei.patrascu@fmi.unibuc.ro>
# Copyright (c) 2021 Bogdan Dumitrescu <bogdan.dumitrescu@upb.ro>
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

import logging

import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds


def graph_to_spectrum_features(
    G,
    FULL_egonets=True,
    IN_egonets=False,
    summable_attributes=[],
    feature_list=None,
    n_values=5,
):
    """Extract spectrum features from input graph: the largest singular values of the associated Laplacians.

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
         Whether full undirected egonets (with radius 1) are considered

     IN_egonets : bool, default=False
         Whether in or out egonets are considered, with respect to the current node.
         Is considered only if FULL_egonets=False.

     summable_attributes : list
         List of edge attributes to be summed as adjacent nodes features.
         The name of the feature is the same as the name of the edge attribute.
         The attributes must be present in all edges; no check is made.
         If the input is a matrix, then summable_attributes must contain column numbers.
         
     feature_list : list of strings
         List of features, each given by its Graphomaly name.
         The possible features are given in :ref:`sec-egonet-spectrum-features`.

     n_values : int, default=5
         Number of largest singular values to be computed.

     Returns
     -------
     node_features: matrix
         Contains features defined by the Laplacian spectrum
         (largest `n_values` singular values) of each egonet.
         Two Laplacian matrices are computed, corresponding to attributes
         cumulated_amount and n_transactions.
         The features on each node are formed by concatenation of
         singular values of the two Laplacian matrices.

     node_ids: vector
         Contains node ids, sorted increasingly, corresponding to the rows
         of node_features.
    """

    if feature_list is None:
        return None, None
    
    # list of possible spectrum features
    valid_egonet_spectrum_features = [
        "f_spectrum_Laplacian",
        "f_spectrum_Laplacian_amount",
        "f_spectrum_Laplacian_average_amount",
        "f_spectrum_Laplacian_n_transactions",
    ]
    # and corresponding edge weights for building the Laplacian
    weights_for_spectrum = [
        None,
        "cumulated_amount",
        "cumulated_amount",     # further processing is explicitly made, since average amount is not stored
        "n_transactions",
    ]

    # These conversions are the same as in graph_to_features.py
    matrix_io = False
    Ns = len(summable_attributes)

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
        # convert dataframe to graph
        G = nx.from_pandas_edgelist(
            df=G,
            source="id_source",
            target="id_destination",
            edge_attr=True,
            create_using=nx.DiGraph,
        )
    elif not isinstance(G, nx.DiGraph):
        logging.warning("Wrong data type for G")

    if not FULL_egonets and IN_egonets:  # reverse graph if in egonets are desired
        G = G.reverse(copy=False)

    logging.info(f"Graph info {nx.info(G)}")

    Nn = G.number_of_nodes()

    # check whether features are valid and count them
    f_good_list = (
        feature_list.copy()
    )  # working copy of the feature list, keeps the found features
    f_bad_list = []
    for feat in feature_list:
        try:
            valid_egonet_spectrum_features.index(feat)
        except ValueError:  # invalid feature
            f_good_list.remove(feat)
            f_bad_list.append(feat)

    if len(f_bad_list) > 0:
        logging.warning("Features not found: %s", f_bad_list)

    # store features in matrix (it's faster)
    node_features = np.zeros((Nn, len(f_good_list) * n_values))
    node_ids = np.zeros(Nn)
    
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

        # compute spectrum with Laplacian as dictated by features
        for i in range(len(f_good_list)):
            feat = f_good_list[i]
            # compute average amount instead of cumulated amount, if necessary
            restore_amount = False
            if feat == "f_spectrum_Laplacian_average_amount":
                restore_amount = True
                for (u,v) in Gs.edges():
                    Gs[u][v]["cumulated_amount"] /= Gs[u][v]["n_transactions"]
            
            k = valid_egonet_spectrum_features.index(feat)
            # compute Laplacian
            L_ego = nx.adjacency_matrix(
                Gs, weight=weights_for_spectrum[k]
            )  # weight requires array of edge weights
            L_ego = L_ego.toarray().astype(float)
            
            D = np.diag(np.sum(L_ego, axis=1))
            L_ego = D - L_ego  # Laplacian matrix is computed

            # Compute SVD of Laplacian matrix
            s = svds(L_ego, n_values, return_singular_vectors=False)
            s = np.sort(s)[::-1]
            node_features[row, i*n_values : i*n_values+len(s)] = s

            # restore cumulated amount
            if restore_amount:
                for (u,v) in Gs.edges():
                    Gs[u][v]["cumulated_amount"] *= Gs[u][v]["n_transactions"]

        node_ids[row] = node
        row = row + 1

    # sort on id
    ii = np.argsort(node_ids)
    node_ids = node_ids[ii]
    node_features = node_features[ii]
    
    if not matrix_io:  # convert matrix to dataframe
        df_columns = []
        for feat in f_good_list:
            for i in range(1, n_values+1):
                df_columns.append(feat + "_" + str(i))
        node_features = pd.DataFrame(node_features, columns=df_columns)


    return node_features, node_ids
