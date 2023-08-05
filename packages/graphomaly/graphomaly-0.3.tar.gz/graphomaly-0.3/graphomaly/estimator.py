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

import logging

logger = logging.getLogger(__name__)

import os

import joblib
import networkx as nx
import numpy as np
import pandas as pd
import pprint
import yaml
from attrdict import AttrDict
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler, RobustScaler, StandardScaler
from threading import Lock

from .grid_search import GridSearch
from .models import ModelsLoader
from .preprocessing.egonet import EgonetFeatures
from .preprocessing.rwalk import RwalkFeatures
from .preprocessing.spectrum import SpectrumFeatures
from .preprocessing.transactions_to_graph import Transactions2Graph
from .voting import VotingClassifier


class GraphomalyEstimator(BaseEstimator):
    """Anomaly detection in graphs.

    The estimator expects a dataset with an underlying graph structure
    and a set of machine learning models and associated parameters
    on which to perform parameter tuning via grid search techniques.
    The result is an ensemble of optimized machine learning models that
    provides labels on existing and new incoming data via voting methods.

    Parameters
    ----------
    config_file: string, default="graphomaly.yaml"
        user provided configuration file that will overwrite the constructor
        provided parameters.

    models_train_all: bool, default=False
        if `True`, performs training on all available models. See
        `ModelsLoader` from `graphomaly.models` for a full list.

    models_subset: list, default=["PyodIForest", "PyodLOF", "PyodOCSVM"]
        if `models_train_all` is `False`, the list of machine learning models to
        use for the Graphomaly estimator.

    models_ctor_kwargs: dictionary, default=None
        constructor arguments for each of the selected machine learning models.

    models_fit_kwargs: dictionary, default=None
        :meth:`fit` arguments for each of the selected machine learning models.

    n_cpus: int, default=1
        number of processors to use when concurrency and parallelism is
        available. Also used during `GridSearch` inside
        `graphomaly.grid_search`.

    results_path: string, default="results"
        directory where to store the trained models for each possible parameter
        configuration provided by the user. The directory is created if it does
        not exist.

    voting: string, default="hard"
        voting method to use for perdictions with the resulting ensemble. See
        the `VotingClassifier` from `graphomaly.voting` for more details.

    voting_normalization: string, default="unify"
        Score normalization method to use.
        See the `VotingClassifier` from `graphomaly.voting` for more details.

    voting_combine: string, default="average"
        Score combining method to use.
        See the `VotingClassifier` from `graphomaly.voting` for more details.

    voting_contamination_rate: float, default=0.001
        Contamination rate to use for soft voting. Applies to the combined score.

    timeout_fit: float or None, default=None
        Maximum timeout (in seconds) for fitting one estimator in the grid search. When None, timeout is disabled.

    scaling_type: string, dict  or None, default=None
        Apply scaling to input data. String, dict or None.
        Can be a string: one of `'MinMaxScaler'`, `'MaxAbsScaler'`,`'RobustScaler'`, `'StandardScaler'`
        or a dict with (key, value) = (estimator name, string), to specify scaling per algorithm.
        Scaler is fit when running fit().

    Attributes
    ----------
    config: attrdict
        if `config_file` was used, this contains the read configuration parameters

    config_file: string
        user provided configuration file

    models_train_all: bool
        whether all available models were used during training

    models_subset: list
        subset of machine learning models to use during training

    models_ctor_kwargs: dictionary
        constructor arguments used for each of the selected machine learning models

    models_fit_kwargs: dictionary
        :meth:`fit` arguments used for each of the selected machine learning models

    n_cpus: int
        number of processors to use

    results_path: string
        directory where trained models are stored

    voting: string
        voting method to used for predictions

    labels_: ndarray
        resulting labels after ensemble voting

    models_list: tuple
        list of models resulting after handling `models_train_all` and `models_subset`
        user options. Used together with `models` when labels are available
        during `GridSearch`

    models: list
        trained models objects for each method in `models_list`. This will
        include the models that performed best during `GridSearch` if labels
        were available during :meth:`fit`, or the models for all parametrizations
        if labels were not available during :meth:`fit`.

    # models_name: list
    #     used together with `models` when labels are not available during `GridSearch`

    feature_names_in_: list
        used during graph preprocessing to store features names

    best_estimators: dict
        best estimator resulted during `GridSearch` for each model

    best_labels_: dict
        associated labels for best estimators resulted during `GridSearch`
        for each model

    best_params: dict
        associated parametrization for best estimators resulted during `GridSearch`
        for each model

    best_score_:  dict
        associated score for best estimators resulted during `GridSearch`
        for each model

    self.scalers_: dict
        dict of scaler object for scaling input data
        key, value = estimator name, sklearn scaler object (or None)

    self.voter_: object
        VotingClassifier object which handles the voting

    self.params_generators: dict of lists
        for each model, a list of generators used to generate parameter combinations
        alongside the parameters defined by `models_fit_kwargs`

    """

    def __init__(
        self,
        config_file="graphomaly.yaml",
        models_train_all=False,
        models_subset=["PyodIForest", "PyodLOF", "PyodOCSVM"],
        models_ctor_kwargs=None,
        models_fit_kwargs=None,
        n_cpus=1,
        results_path="results",
        voting="hard",
        voting_normalization = "unify",
        voting_combine="average",
        voting_contamination_rate=0.001,
        timeout_fit = None,
        scaling_type = None
    ):
        self.config_file = config_file
        self.models_train_all = models_train_all
        self.models_subset = models_subset
        self.models_ctor_kwargs = models_ctor_kwargs
        self.models_fit_kwargs = models_fit_kwargs
        self.n_cpus = n_cpus
        self.results_path = results_path
        self.voting = voting
        self.voting_normalization = voting_normalization
        self.voting_combine = voting_combine
        self.voting_contamination_rate = voting_contamination_rate
        self.timeout_fit = timeout_fit
        self.scaling_type = scaling_type

        self.labels_ = []

        self.models_list = []
        self.models = []
        # self.models_name = []
        self.feature_names_in_ = []

        self._model_is_fitted = False

        # tune
        self.best_estimators = {}
        self.best_labels_ = {}
        self.best_params = {}
        self.best_score_ = {}

        self.scalers_ = {}

        # Create a VotingClassifier placeholder, will be initialized later, after
        self.voter = None

        # For each model, a list of generators used to generate parameter combinations
        # alongside the parameters defined by `models_fit_kwargs`
        self.params_generators = {}

        logger.setLevel(logging.INFO)


        # Overwrite from configuration file
        if self.config_file and os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.config = AttrDict(yaml.safe_load(f))

                self.models_train_all = self.config.models.train_all
                self.models_subset = self.config.models.subset
                self.models_ctor_kwargs = self.config.models.ctor_kwargs if 'ctor_kwargs' in self.config.models else {}
                self.models_fit_kwargs = self.config.models.fit_kwargs
                self.results_path = self.config.results.path
                self.timeout_fit=self.config.timeout_fit if 'timeout_fit' in self.config else self.timeout_fit
                #self.voting = self.config.voting
                # Set individual voting parameters from config
                self.voting = self.config.voting.method if 'method' in self.config.voting else self.voting   # self.voting is a string
                self.voting_normalization = self.config.voting.normalization if 'normalization' in self.config.voting else self.voting_normalization
                self.voting_combine = self.config.voting.combine if 'combine' in self.config.voting else self.voting_combine
                self.voting_contamination_rate = self.config.voting.contamination_rate if 'contamination_rate' in self.config.voting else self.voting_contamination_rate

        # Ovewrite individual contamination_rate with the global voting_contamination_rate
        for estim_name, estim_fitkw in self.models_fit_kwargs.items():
            estim_fitkw['contamination'] = self.voting_contamination_rate

        os.makedirs(self.results_path, exist_ok=True)

        self._get_models_list()

        # Create `scaling_type` dict for estimators
        #
        # `Scaling_type` handling:
        # - if constructor argument `scaling_type` is provided, it is used for all estimators
        # - otherwise, use values from config file
        #   - use the individual `scaling_type` defined for each estimator
        #   - otherwise, use the global scaling_type in the file, if provided
        # `scaling-type` can be a string, or a dict with key = estimators and value = string

        self.scaling_type_dict = {}
        if isinstance(self.scaling_type, dict):
            # If already a dict, use as is, but check that all algorithms are specified
            algs_missing = [alg for alg in self.models_list if alg not in self.scaling_type]
            if len(algs_missing) != 0:
                raise ValueError(f"scaling_type is given as a dict, but not all algorithms are specified ({algs_missing})")

            self.scaling_type_dict = self.scaling_type
        elif self.scaling_type is not None:
            # Same scaling for all estimators
            self.scaling_type_dict = {algorithm:self.scaling_type for algorithm in self.models_list}
        else:
            # Use values from config file, if exists

            for algorithm in self.models_list:

                if self.models_fit_kwargs is not None and 'scaling_type' in self.models_fit_kwargs[algorithm]:
                        scal = self.models_fit_kwargs[algorithm]['scaling_type']
                elif hasattr(self, 'config') and 'scaling_type' in self.config:
                        scal = self.config['scaling_type']
                else:
                    scal = None

                self.scaling_type_dict[algorithm] = scal

        logger.info(f"Scaling configuration: {pprint.pformat(self.scaling_type_dict)}")

        # Clean fit_kwargs of any `scaling_type` parameter, regardless if used or not,
        #  so it doesn't reach the actual estimator object
        if self.models_fit_kwargs is not None:
            for algorithm in self.models_list:
                self.models_fit_kwargs[algorithm].pop('scaling_type', None)

    def load(self):
        """Virtual method for loading the dataset."""
        raise NotImplementedError("Must override load() for your dataset")

    def preprocess(self, X, y, type=None, **kwargs):
        """Apply preprocessing operations on raw dataset.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            The raw training dataset consisting of transactions list or graph

        y: array-like of shape (n_samples, )
            The ground truth for training dataset.

        type: string
            Preprocessing steps required. Depending on the input, the possible
            preprocessing actions are:

            * `'transactions_to_features'`: see  :ref:`sec-transaction-list-to-features` (TODO)
            * `'graph_to_features'`: see :ref:`sec-graph-to-features`
            * `'transactions_to_graph_to_features'`: combines the operations from
                :ref:`sec-transaction-list-to-graph` and :ref:`sec-graph-to-features`

        Keyword Args: dictionary
            The keyword args contains a dictionary consisting of two entries

            * to_graph_args: dictionary
                Contains fit `kwargs` for `preprocessing.transactions_to_graph`
                module
            * to_feature_args: dictionary
                Available key values:

                * algorithms: list of strings
                    Possible elements: `'egonet'`, `'rwalk'`, `'spectrum'`
                * algorithms_args: dictionary
                    Possible elements: '`ctor_args'` and `'fit_args'`

                    * ctor_args: dictionary
                        Represents arguments passed to the algorithm's constructor.
                    * fit_args: dictionary
                        Represents options passed to the fit method.

        Returns
        -------
        X: ndarray
            The preprocessed training dataset.

        y: ndarray
            The preprocessed labels.

        G: ndarray
            The graph associated to the raw training dataset.

        See also
        --------
        tests.test_synthetic_preprocessing : example of building and passing kwargs
        """
        G = None

        # if type == "transactions_to_features":
        if type == "graph_to_features":
            if y is not None:
                y = self._preprocess_labels(X, y, type)
            X = self._process_graph_to_features(X, **kwargs)
        elif type == "transactions_to_graph_to_features":
            to_graph_args = kwargs["to_graph_args"]
            to_features_args = kwargs["to_features_args"]

            if y is not None:
                y = self._preprocess_labels(X, y, type)
            t2g = Transactions2Graph()
            G = t2g.fit_transform(X, **to_graph_args)

            X = self._process_graph_to_features(G, **to_features_args)
        return X, y, G

    def _preprocess_labels(self, X, y, type):
        if type == "transactions_to_graph_to_features" or type == "graph_to_features":
            Xy = np.c_[X[:, 0], X[:, 1], y]
            Xy = pd.DataFrame(data=Xy, columns=["source", "destination", "labels"])

            gXy = nx.from_pandas_edgelist(
                df=Xy,
                source="source",
                target="destination",
                edge_attr=True,
                create_using=nx.MultiDiGraph,
            )

            y_true_nodes = np.zeros((gXy.number_of_nodes(),), dtype=int)
            nodes_array = np.array(gXy.nodes())
            for (i, j, label) in gXy.edges.data("labels"):
                if label >= 1:
                    index = np.where(nodes_array == i)[0][0]
                    y_true_nodes[index] = 1
                    index = np.where(nodes_array == j)[0][0]
                    y_true_nodes[index] = 1

            # sort on node id
            ii = np.argsort(nodes_array)
            y = y_true_nodes[ii]

        return y

    def _process_graph_to_features(self, G, **kwargs):
        algorithms = kwargs["graph_algorithms"]
        algorithms_args = kwargs["graph_algorithms_args"]

        all_features = []
        for i, algo in enumerate(algorithms):
            ctor_args = algorithms_args[i]["ctor_args"]
            fit_args = algorithms_args[i]["fit_args"]
            if algo == "egonet":
                ego = EgonetFeatures(**ctor_args)
                features = ego.fit_transform(G, **fit_args)
                features_names_in = ego.feature_names_in_
            elif algo == "rwalk":
                rwalk = RwalkFeatures(**ctor_args)
                features = rwalk.fit_transform(G, **fit_args)
                features_names_in = rwalk.feature_names_in_
            elif algo == "spectrum":
                spectrum = SpectrumFeatures(**ctor_args)
                features = spectrum.fit_transform(G, **fit_args)
                features_names_in = spectrum.feature_names_in_
            all_features.append(features)
            self.feature_names_in_.append(features_names_in)

        return np.concatenate(all_features, axis=1)

    def _get_params(self, algorithm, n_features):
        model_kwargs = {}
        if self.models_ctor_kwargs is not None:
            if algorithm in self.models_ctor_kwargs:
                model_kwargs = self.models_ctor_kwargs[algorithm]

        fit_kwargs = {}
        if self.models_fit_kwargs is not None:
            if algorithm in self.models_fit_kwargs:
                fit_kwargs = self.models_fit_kwargs[algorithm]

        # Setting the correct number of decoder neurons after preprocessing.
        if "decoder_neurons" in model_kwargs:
            model_kwargs["decoder_neurons"][-1] = n_features

        if "input_dim" in model_kwargs:
            model_kwargs["input_dim"] = n_features

        return model_kwargs, fit_kwargs

    def _get_models_list(self):
        if self.models_train_all:
            self.models_list = ModelsLoader.models   # That's a dictionary {'name':object} (... I think)
        else:
            self.models_list = self.models_subset    # That's a dictionary {'name': parameter dict} from the config file

    def fit(self, X, y=None, refit=False):
        """Train anomaly detection models on samples in `X`.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to fit the methods in `models_list`

        y: array-like of shape (n_samples, )
            The ground truth for samples `X`. If `None` then the best estimator
            across parameter opotions will not be sought.

        refit: boolean
            Reuse saved experiments (refit=False) or run them again (refit=True). Defaults to False.

        Returns
        -------
        self: object
            Fitted estimator.

        See also
        --------
        tests.test_synthetic:
            example of performing fit on synthetic
            generated data on a small subset of methods and parameters list.
        """
        if refit is False and self._model_is_fitted is True:
            return self

        self.tune(X, y, refit=refit)
        self._model_is_fitted = True

        return self

    def refit(self, X, y=None):
        """Retrain anomaly detection models on samples in `X`.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to fit the methods in `models_list`

        y: array-like of shape (n_samples, )
            The ground truth for samples `X`. If `None` then the best estimator
            across parameter opotions will not be sought.

        Returns
        -------
        self: object
            Re-Fitted estimator.
        """
        # if self._model_is_fitted is False:
            # return

        self.tune(X, y, refit=True)
        self._model_is_fitted = True

    def load_cached(self, X, y=None):
        """Like fit(), but only loads estimators cached to disk, and doesn't fit any new estimator.

        Args:
            X (_type_): _description_
            y (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self.tune(X, y, refit=False, only_cached=True)
        self._model_is_fitted = True

        return self

    def predict(self, X, voting=None, normalization=None, combine=None):
        """Perform anomaly detection on samples in `X`.

        A wrapper around `vote`.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to perform anomaly detection

        voting: string
            Voting method. See `graphomaly.voting` for available options.

        normalization: string
            Normalization method for individual estimator's scores.
            See `graphomaly.voting` for available options.

        combine: string
            Combination method of estimator's scores.
            See `graphomaly.voting` for available options.


        Returns
        -------
        y: array-like of shape (n_samples, ) or list(array-like of shape (n_samples, ))
            If combine == 'no', returns a list of predicted labels for each underlying estimator. The estimator order is the same as returned by get_estimator_params()
            If combine != 'no', returns the predicted labels

        See also
        --------
        tests.test_synthetic: example of predicting on synthetic generated data.
        """
        #self.labels_ = self.vote(X, voting=voting, normalization=normalization, combine=combine)
        #return self.labels_

        # Do not store in labels_
        # predict() should not change the object, only fit()
        return self.vote(X, voting=voting, normalization=normalization, combine=combine)

    def predict_proba(self, X, normalization=None, combine=None):
        """Returns the normalized scores for data in X

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to perform anomaly detection

        normalization: string
            Normalization method for individual estimator's scores.
            See `graphomaly.voting` for available options.

        combine: string
            Combination method of estimator's scores.
            See `graphomaly.voting` for available options.

        Returns
        -------
        y: array-like of shape (n_samples, n_classes) or list(array-like of shape (n_samples, n_classes))
            If combine == 'no', returns a list of predicted_probas for each underlying estimator. The estimator order is the same as returned by get_estimator_params()
            If combine != 'no', returns the combined predicted_probas
        """

        normalization = normalization if normalization is not None else self.voting_normalization
        combine = combine if combine is not None else self.voting_combine

        return self.voter.predict_proba(X, normalization=normalization, combine=combine)

    def vote(self, X, voting=None, normalization=None, combine=None):
        """Perform anomaly detection on samples in `X` using Graphomaly's
        `VotingClassifier`.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to perform anomaly detection

        voting: string
            Voting method. See `graphomaly.voting` for available options.

        normalization: string
            Normalization method for individual estimator's scores.
            See `graphomaly.voting` for available options.

        Returns
        -------
        y: array-like of shape (n_samples, )
            The predicted labels

        See also
        --------
        tests.test_synthetic_voting:
            example of trying all available voting methods
        """
        # Use arguments provided in this call, or fallback to default values set at instantiation
        # Don't overwrite parameters set at instantiation
        # Current arguments method should be used for current prediction only
        #
        #if voting:
        #    self.voting = voting

        voting = voting if voting is not None else self.voting
        normalization = normalization if normalization is not None else self.voting_normalization
        combine = combine if combine is not None else self.voting_combine

        return self.voter.predict(X, voting=voting, normalization=normalization, combine=combine)

    def tune(self, X, y=None, refit=False, only_cached=False):
        """Perform parameter tuning on samples in `X` using Graphomaly's
        `GridSearch`.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to perform parameter tuning for the `models_list`

        y: array-like of shape (n_samples, )
            The ground truth for samples `X`. If `None` then the best estimator
            information will not be set.

        refit: bool, default=False
            If this is a refit, clean existing model before proceeding with
            GridSearch.

        Returns
        -------
        self: object
            Fitted estimator.

        See also
        --------
        tests.test_synthetic_gridsearch:
            example of performing parameter tuning
            on a small subset of methods and parameters list.
        """

        # Save the input X before scaling
        X_input = X

        for algorithm in self.models_list:
            model_kwargs, fit_kwargs = self._get_params(algorithm, X.shape[1])

            # Merge 'common' kwargs, with lower priority
            if 'common' in self.models_fit_kwargs:
                fit_kwargs = {**self.models_fit_kwargs['common'], **fit_kwargs}

            # Create and fit scaler object. Same scaler will be used in later calls to predict() and predict_proba()
            #
            # Scaling cannot be done in preprocessing(), because there we don't know if we preprocess the data
            # in order to (i) fit, where we need to learn a new scaler, (ii) predict, where we just need to use the old scaler,
            # or (iii) refit, where we have an old scaler but we don't want to use it

            # Apply on original X, not on the X transformed at the previous iteration.

            if self.scaling_type_dict[algorithm] == "MinMaxScaler":
                self.scalers_[algorithm] = MinMaxScaler().fit(X_input)
                X = self.scalers_[algorithm].transform(X_input)
            elif self.scaling_type_dict[algorithm]  == "MaxAbsScaler":
                self.scalers_[algorithm] = MaxAbsScaler().fit(X_input)
                X = self.scalers_[algorithm].transform(X_input)
            elif self.scaling_type_dict[algorithm]  == "RobustScaler":
                self.scalers_[algorithm] = RobustScaler().fit(X_input)
                X = self.scalers_[algorithm].transform(X_input)
            elif self.scaling_type_dict[algorithm]  == "StandardScaler":
                self.scalers_[algorithm] = StandardScaler().fit(X_input)
                X = self.scalers_[algorithm].transform(X_input)

            clf = ModelsLoader.get(algorithm, **model_kwargs)
            if hasattr(clf, "save"):  # tf model detected
                clf_type = "tensorflow"
            else:
                clf_type = "sklearn"

            search = GridSearch(
                clf,
                fit_kwargs,
                n_cpus=self.n_cpus,
                datadir=self.results_path,
                clf_type=clf_type,
                refit=refit,
                clf_algorithm = algorithm,
                clf_model_kwargs = model_kwargs,
                params_generators = self.params_generators[algorithm] if algorithm in self.params_generators else [],
                timeout_fit=self.timeout_fit
            )
            search.fit(X, y, only_cached=only_cached)

            if y is None:
                #self.models_name.extend([algorithm]) # algorithm is taken from self.models_list, we just duplicate?
                self.models.extend(search.estimators_)
                self.known_best_estimator = False
            else:
                self.best_params[algorithm] = search.best_params_
                self.best_estimators[algorithm] = search.best_estimator_
                self.best_labels_[algorithm] = search.labels_
                self.best_score_[algorithm] = search.best_score_
                self.known_best_estimator = True

                self.models.append(search.best_estimator_)

                logger.info(
                    f"Best params for {algorithm}[{search.best_score_}]: "
                    f"{search.best_params_}"
                )

        # Initialize the VotingClassifier object
        # Some estimators might be None (e.g. no fit() for specified model actually finished in time). Keep only the non-None ones.
        voting_estimators = [(name, obj) for name, obj in zip(self.models_list, self.models) if obj is not None]

        self.voter = VotingClassifier(estimators=voting_estimators,
                voting=self.voting,
                normalization=self.voting_normalization,
                combine=self.voting_combine,
                contamination_rate=self.voting_contamination_rate,
                available_normalizations=[self.voting_normalization],
                available_combines=[self.voting_combine],
                scalers=self.scalers_)

        self.voter.fit(X_input,y)

        return self

    def decision_function(self, X):
        """Calls decision_function(X) for all the contained estimators, and returns all the results.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to perform decision_function()

        Returns
        -------
        anomaly_scores: numpy array of shape (n_estimators, n_samples, )
            The anomaly score of the input samples.

        """

        return np.concatenate(
            [mdl.decision_function(self.scale_for_estimator(X, mdl_name)) for (mdl_name, mdl) in zip(self.models_list, self.models)], \
            axis=0)

    def get_estimator_params(self):
        """Returns a list of estimators' names and params

        Returns
        -------
        voting_estimators: list(tuple(str, dict)
            A list of tuples (estimator_name, estimator.get_params(), for all estimators.
        """

        # Some estimators might be None (e.g. no fit() for specified model actually finished in time). Keep only the non-None ones.
        voting_estimators = [(name, obj.get_params()) for name, obj in zip(self.models_list, self.models) if obj is not None]

        return voting_estimators

    def scale_for_estimator(self, X, estimator_name):
        """Scale data for given estimator

        Args:
            X (ndarray): Data matrix
            estimator_name (str): Name of estimator

        Returns:
            ndarray: Scaled data
        """

        # Scale data
        if estimator_name in self.scalers:
            X = self.scalers_[estimator_name].transform(X)
            logger.debug(f"Scaling with {self.scalers[estimator_name].__class__.name}, estimator {estimator_name}, data shape {X.shape}")
        else:
            logger.debug(f"No scaling done, estimator {estimator_name}, data shape {X.shape}")

        return X

    def save(self, filepath):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath):
        return joblib.load(filepath)


class GraphomalySafeEstimator:
    """Wrapper to ensure that training the estimator can be done in parallel
    with predicting.

    Internally delegates the training to a second GraphomalyEstimator object,
    so that the original GraphomalyEstimator can keep predicting().
    When training is done, the first estimator re-loads the trained
    estimators from the disk.

    There are two locks:

    1. Memory lock:
      - guards the estimator objects loaded in the memory
      - ensures that `load_cached()`, `predict()` and `predict_proba()`
        are mutually exclusive when they access the object
    2. Folder lock:
      - guards the folder where the individual estimators are saved during training
      - ensures that `fit()`, `refit()` and `load_cached()` are mutually exclusive

    `fit()` and `refit()` need only the Folder lock.
    `predict()` and `predict_proba()` need only the Memory lock.
    `load_cached()` needs both the Memory lock and the Folder lock .

    One of (`fit()` or `refit()`) can run in parallel
    with one of (`predict()` and `predict_proba()`)
    """

    def __init__(self, *args, **kwargs) -> None:
        self.predictor = GraphomalyEstimator(*args, **kwargs)
        self.trainer   = GraphomalyEstimator(*args, **kwargs)

        self.memory_lock = Lock()
        self.folder_lock = Lock()

    def fit(self, *args, **kwargs):
        with self.folder_lock:
            self.trainer.fit(*args, **kwargs)

        # Acquires lock internally
        return self.load_cached(*args, **kwargs)

    def refit(self, *args, **kwargs):
        with self.folder_lock:
            self.trainer.refit(*args, **kwargs)

        # Acquires lock internally
        return self.load_cached(*args, **kwargs)

    def load_cached(self, *args, **kwargs):
        with self.memory_lock, self.folder_lock:
            return self.predictor.load_cached(*args, **kwargs)

    def predict(self, *args, **kwargs):
        with self.memory_lock:
            return self.predictor.predict(*args, **kwargs)

    def predict_proba(self, *args, **kwargs):
        with self.memory_lock:
            return self.predictor.predict_proba(*args, **kwargs)

    def preprocess(self, *args, **kwargs):
        return self.predictor.preprocess(*args, **kwargs)

    def get_estimator_params(self, *args, **kwargs):
        return self.predictor.get_estimator_params(*args, **kwargs)

    @property
    def _model_is_fitted(self):
        return self.predictor._model_is_fitted
