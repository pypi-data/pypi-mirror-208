import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class Transactions2Graph(BaseEstimator, TransformerMixin):
    """Transform transaction list to graph.

    Given a dataframe or matrix containing a transaction list, with at least the
    following columns (if dataframe, the names of the columns can be arbitrary)

    * source id (int)
    * destination id (int)
    * amount of money transferred from source to destination

    transform it into a graph by cumulating the amounts between two ids and
    counting the associated number of transactions.

    Attributes
    ----------
    feature_names_in_ : list of strings
        List of column names in graph description.

    n_output_features_ : int
        Number of graph columns.

    Example
    -------
    Assume L is a matrix containing a transactions list; each row represents a transaction.
    The first three columns are: id_source, id_destination, amount.
    The following code transforms the list into a graph.

    .. code-block:: python

        from graphomaly.preprocessing.transactions_to_graph import Transactions2Graph
        it2g = Transactions2Graph()
        G = it2g.fit_transform(L)

    The matrix G containing the graph has 4 columns: id_source, id_destination,
    cumulated_amount, n_transactions.
    """

    def __init__(self):
        self.column_names = None
        self.summable_attributes = None
        self.summable_attributes_out_names = None

        self.feature_names_in_ = None
        self.n_output_features_ = 0

    def fit(
        self,
        X,
        y=None,
        column_names=None,
        summable_attributes=None,
        summable_attributes_out_names=None,
    ):
        """
        Store column names to be computed by :meth:`transform`.

        Parameters
        ----------
        column_names: list of strings
            List of column names for source id, destination id and amount.

        summable_attributes : list of strings or int
            List of transaction attributes (columns) to be summed as edge features.
            (Same behavior as for the amount column.)

        summable_attributes_out_names : list of strings
            Names of the edge attributes in the graph.
            If not given, the same names as in summable_attributes are used.

        """
        if column_names is None:
            self.column_names = ["id_source", "id_destination", "amount"]
        else:
            self.column_names = column_names

        self.summable_attributes = summable_attributes
        if (
            self.summable_attributes is not None
        ):  # ignore names if there are no summable attributes
            self.summable_attributes_out_names = summable_attributes_out_names

        return self

    def transform(self, X):
        """
        Transform transaction list to graph, using the columns described by :meth:`fit`.

        Parameters
        ----------
        X : DataFrame or matrix
            List of transactions having at least three columns: source id, destination id and amount.
            If dataframe, the names of these columns are those from column_names.
            If matrix, the first three columns are used.

        Returns
        -------
        graph : DataFrame or matrix
            Transaction list as a graph. It has the same datatype as X.
            If dataframe, it has the following columns with fixed names:

            * `'id_source'`: source node number
            * `'id_destination'`: destination node number
            * `'cumulated_amount'`: the cumulated amount of transactions from source to destination node
            * `'n_transactions'`: number of transactions between the two nodes

            Other attributes are built as sums over transactions, as indicated by summable_attributes.
            If matrix, its columns have the meanings above, in exactly this order.
        """

        # BD 4.09.2021, 27.02.2022

        if self.summable_attributes is not None:
            if self.summable_attributes_out_names is None:
                # preserve other atrributes names, if not given
                self.summable_attributes_out_names = self.summable_attributes.copy()
                # convert to string (to cover the numerical case)
                self.summable_attributes_out_names = [
                    str(i) for i in self.summable_attributes_out_names
                ]

            summable_attributes_str = [
                str(i) for i in self.summable_attributes
            ]  # like above

        matrix_io = False
        if isinstance(X, np.ndarray):  # if matrix, convert to dataframe
            matrix_io = True
            c_list = [0, 1, 2]
            c_names = self.column_names
            if self.summable_attributes is not None:
                c_list += self.summable_attributes.copy()
                c_names += summable_attributes_str
            X = pd.DataFrame(X[:, c_list], columns=c_names)

        group_id = X.groupby([self.column_names[0], self.column_names[1]])
        graph = (
            group_id[self.column_names[2]]
            .sum()
            .to_frame(name="cumulated_amount")
            .reset_index()
        )
        graph["n_transactions"] = np.array(group_id.size())
        graph.rename(
            columns={
                self.column_names[0]: "id_source",
                self.column_names[1]: "id_destination",
            },
            inplace=True,
        )
        if self.summable_attributes is not None:
            graph[self.summable_attributes_out_names] = np.array(
                group_id[summable_attributes_str].sum()
            )

        self.feature_names_in_ = [
            "id_source",
            "id_destination",
            "cumulated_amount",
            "n_transactions",
        ]
        if self.summable_attributes is not None:
            self.feature_names_in_ += self.summable_attributes_out_names

        self.n_output_features_ = graph.shape[1]

        if matrix_io:  # convert back to matrix
            graph = graph.to_numpy()

        return graph
