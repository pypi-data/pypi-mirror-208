# Copyright (c) 2022 Andra Băltoiu <andra.baltoiu@gmail.com>
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
logger = logging.getLogger(__name__)

import inspect
import itertools

import joblib
import numpy as np
from pyod.models.combination import aom, average, maximization, median, moa
from pyod.utils.utility import standardizer
from sklearn.base import ClassifierMixin
from sklearn.ensemble._voting import _BaseVoting
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.utils.metaestimators import available_if
from sklearn.utils.validation import check_is_fitted

from .normalizations import MinMaxScaler, QuantileTransformer, GaussScalingTransformer
from .models.autoencoder import Autoencoder
from .models.vae import VAE

#==========================================
# How to use VotingClassifier:
#
#  Ensemble:
#    predict():           ensemble prediction            input X, output labels, combined
#    predict_proba():     ensemble score                 input X, output scores, combined
#
#  Individual estimators:
#    transform():         individual prediction/scores     input X, output labels or scores, each. Wrapper of _predict() or _collect_probas()
#      _predict():        individual prediction            input X, output labels, each
#      _collect_probas(): individual scores                input X, output scores, each
#==========================================

class VotingClassifier(ClassifierMixin, _BaseVoting):
    """Ensemble voting of multiple estimators

    How to use VotingClassifier:

    Ensemble:

    - predict():           ensemble prediction            input X, output labels, combined
    - predict_proba():     ensemble score                 input X, output scores, combined

    Individual estimators:

    - transform():         individual prediction/scores     input X, output labels or scores, each.
                           Wrapper of _predict() or _collect_probas()
    - _predict():          individual prediction            input X, output labels, each
    - _collect_probas():   individual scores                input X, output scores, each
    """

    # Class-level option lists
    available_normalizations = ['raw', 'default', 'linear', 'unify', 'gaussian', 'standard']  # and 'no'
    available_combines = ["average", "maximization", "median", "aom", "moa"]                  # and 'no

    def __init__(
        self,
        estimators,
        *,
        voting="hard",
        normalization='default',
        combine='average',
        weights=None,
        n_jobs=None,
        flatten_transform=True,
        verbose=False,
        contamination_rate=None,
        available_normalizations=None,
        available_combines=None,
        scalers = {}
    ):
        super().__init__(estimators=estimators)
        self.voting = voting
        self.normalization = normalization
        self.combine = combine
        self.weights = weights
        self.n_jobs = n_jobs
        self.flatten_transform = flatten_transform
        self.verbose = verbose
        self.contamination_rate = contamination_rate
        self.available_normalizations = available_normalizations if available_normalizations is not None else VotingClassifier.available_normalizations
        self.available_combines = available_combines if available_combines is not None else VotingClassifier.available_combines
        self.scalers = scalers

        # Create in fit()
        #self.estimators_ = []  # This makes _model_is_fitted() always return True ?
        #self.normalizers_ = []   # Will store a list of dicts with fitted normalizers

    def fit(self, X, y=None):
        """Train anomaly detection models on samples in `X`, with voting.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to fit the methods

        y: array-like of shape (n_samples, )
            The ground truth for samples `X`.

        Returns
        -------
        self: object
            Fitted VotingClassifier object.
        """

        self.estimators_ = []
        self.normalizers_ = []   # Will store a list of dicts with fitted normalizers
        self.threshold_dict_ = {}

        for clf_name, clf in self.estimators:

            # Scale data
            Xscaled = self.scale_for_estimator(X, clf_name)

            if not self._model_is_fitted(clf, Xscaled[0]):
                clf.fit(Xscaled)
            self.estimators_.append(clf)

        #self.__sklearn_is_fitted__() # ?

        # Fit individual normalizers
        self.fit_normalizers(X)

        # Fit thresholds for combination
        self.fit_threshold(X)

        return self

    def fit_normalizers(self, X):
        """Train the outlier scores normalizers on samples in `X`.
        Normalizers are used in voting to bring scores from all models in the same range.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to fit the methods

        Returns
        -------
        self: object
            Fitted VotingClassifier object.
        """

        for est_name, clf in self.estimators:

            # Compute decision scores for each estimator
            if hasattr(clf, 'decision_scores_'):
                logger.debug(f"VotingClassifier fit(): using {est_name} decision_scores_")
                decision_scores = clf.decision_scores_
            else:
                logger.debug(f"VotingClassifier fit(): computing decision scores for {est_name}")
                Xscaled = self.scale_for_estimator(X, est_name)
                decision_scores = cached_decision_function(clf, Xscaled)
            decision_scores = np.reshape(decision_scores, (-1,1))

            # Fit different normalizers for each estimator,
            # and append them to the normalizers list
            normalizers = {}
            normalizers['raw'] = StandardScaler(with_mean=False, with_std=False)  # does nothing
            normalizers['raw'].fit(decision_scores)
            normalizers['linear'] = MinMaxScaler()
            normalizers['linear'].fit(decision_scores)
            normalizers['unify'] = GaussScalingTransformer()
            normalizers['unify'].fit(decision_scores)
            normalizers['standard'] = StandardScaler()
            normalizers['standard'].fit(decision_scores)
            #
            normalizers['default'] = None
            normalizers['gaussian'] = normalizers['unify']   # same thing
            #
            self.normalizers_.append(normalizers)

        return self

    def fit_threshold(self, X):
        """Train the threshold for anomaly detection on samples in `X`, for the post-voting combined score.

        Parameters
        ----------
        X: array-like of shape (n_samples, n_features)
            samples on which to fit the methods

        Returns
        -------
        self: object
            Fitted VotingClassifier object.
        """

        # Fit threshold for each tuple (normalization, combine)
        # It's not very efficient to call predict_proba for all possible combinations. Turn on caching?
        for norm, comb in itertools.product(self.available_normalizations, self.available_combines):
            try:
                combined_score = self.predict_proba(X, normalization=norm, combine=comb,
                                                    use_decision_scores=True)[:,1]
                self.threshold_dict_[(norm, comb)] = np.quantile(combined_score, 1-self.contamination_rate)
            except Exception as e:
                logger.warning(f'Caught exception in fit_threshold(), norm={norm}, comb={comb}, exception: {e}')

        logger.debug(f'self.threshold_dict_ = {self.threshold_dict_}')

        return self

    def _model_is_fitted(self, model, X):
        """Checks if model object has any attributes ending with an underscore.

        Notes
        -----
        **References:**
        Scikit-learn glossary on `fitted'
        https://scikit-learn.org/dev/glossary.html#term-fitted

        Stack-Overflow answer for the best way to check if a model is fitted.
        https://stackoverflow.com/a/48046685
        """
        try:
            return 0 < len(
                [
                    k
                    for k, v in inspect.getmembers(model)
                    if k.endswith("_") and not k.startswith("__")
                ]
            )
        except ValueError:  # keras compiled model
            try:
                model.predict(X[None, :])  # expecting a single vector
                return True
            except NotFittedError:
                return False

    def __sklearn_is_fitted__(self) -> bool:
        return getattr(self, "fitted_", True)

    def __fix_saved_tf_scores(self, X, method):
        clf = method[1]

        # Scale
        X = self.scale_for_estimator(X, method[0])

        if "Custom>Autoencoder" in str(type(method[1])):
            from graphomaly.models.autoencoder import Autoencoder

            Y = clf.predict(X)
            scores = Autoencoder._compute_scores(X, Y)
        elif "Custom>VAE" in str(type(method[1])):
            from graphomaly.models.vae import VAE

            Y = clf.predict(X)
            scores = VAE._compute_scores(X, Y)
        else:
            scores = clf.predict(X)  # i.e. give-up!

        labels = (scores > clf.tf_threshold.numpy()).astype("int")

        scaler = MinMaxScaler()
        scaler.fit(scores.reshape(-1, 1))
        probs = np.zeros([X.shape[0], 2])
        probs[:, 1] = scaler.transform(scores.reshape(-1, 1)).squeeze()
        probs[:, 0] = 1 - probs[:, 1]

        return scores, labels, probs

    def predict(self, X, voting=None, normalization=None, combine=None):
        """Predict labels for samples in X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The input samples.
        voting: str
            Type of voting: 'hard', 'soft', 'no', or None
            'no': do no voting, return instead a list of labels from each underlying estimator
            Argument value takes precedence over the value configured at instantiation.
            If voting=None, use voting type specified at instantiation.
        normalization: str
            How to transform the individual scores of each estimator. Passed to _collect_probas() internally.
            Only used for soft voting.
        combine: str
            How to combine the transformed scores of each estimator
            'average' (or None), 'maximization', 'median', 'aom', 'mao'
            Only used for soft voting.

        Returns
        -------
        y: array-like of shape (n_samples, ) or list(array-like of shape (n_samples, ))
            If combine == 'no', returns a list of predicted labels for each underlying estimator. The estimator order is the same as in initialization.
            If combine != 'no', returns the predicted labels
        """

        # Use provided arguments, and fallback to instantiation values
        voting = voting if voting is not None else self.voting
        normalization = normalization if normalization is not None else self.normalization
        combine = combine if combine is not None else self.combine

        check_is_fitted(self)

        # soft and hard votings from sklearn
        if voting == "soft":
            #maj = np.argmax(self.predict_proba(X, normalization=normalization, combine=combine), axis=1)
            if (normalization,combine) in self.threshold_dict_:
                scores = self.predict_proba(X, normalization=normalization, combine=combine)[:,1]
                maj = scores > self.threshold_dict_[(normalization, combine)]
                maj = maj.astype(int)
            else:
                raise ValueError(f"No threshold available for soft voting with normalization={normalization}, combine={combine}")

        elif voting == "hard":  # 'hard' voting
            predictions = self._predict(X)
            maj = np.apply_along_axis(
                lambda x: np.argmax(np.bincount(x, weights=self._weights_not_none)),
                axis=1,
                arr=predictions,
            )
            #  maj = self.le_.inverse_transform(maj)

        elif voting == "no":  # No voting, return hard prediction results of each underlying estimator
            maj = self._predict(X)

        # Always returns labels.
        # If you want to return scores, use predict_proba()
        return maj

    def fit_predict(self, X, y):
        """Call fit() and then predict()
        """
        return self.fit(X, y).predict(X)

    def _collect_probas(self, X, normalization=None, use_decision_scores = False):
        """Collect results estimators predict_probas(), with configurable normalizations

        If use_decision_scores is True, we skip calling predict_proba() or
        decision_function() and we collect the estimators' decision_scores_,
        which are then regularized explicitly.
        Use this option only when fitting for the train data, not for the test data.
        """

        # return np.asarray([clf.predict_proba(X) for clf in self.estimators_])

        probas = []
        for (method_name, method_obj),normalizers in zip(self.estimators, self.normalizers_):

            # Decide which normalization method to use for scores
            # Use provided argument or fallback to self.normalization
            normalization = normalization if normalization is not None else self.normalization

            # We could also pass a dictionary indicating normalization type for each method
            if isinstance(normalization, dict):
                if method_name in self.normalization:
                    normalization = self.normalization[method_name]
                elif 'default' in self.normalization:
                    normalization = self.normalization['default']
                else:
                    raise ValueError(f"Normalization {normalization} not understood")

            # Scale data
            Xscaled = self.scale_for_estimator(X, method_name)

            # Get probas
            done = False

            # Attempt to use estimator's predict_proba() with method 'linear' or 'unify'
            if not use_decision_scores and \
               (normalization == 'default' or normalization == 'linear' or normalization == 'unify') and \
               hasattr(method_obj, 'predict_proba'):

                try:
                    logger.debug(f'Voting {self.voting}: predict_proba({normalization}): {method_obj}')
                    if normalization == 'default':
                        #probas_pred = method_obj.predict_proba(X)
                        probas_pred = cached_predict_proba(obj=method_obj, X=Xscaled)
                    else:
                        #probas_pred = method_obj.predict_proba(X, method=normalization)
                        probas_pred = cached_predict_proba(obj=method_obj, X=Xscaled, method=normalization)
                    done = True
                except Exception as e:
                    logger.debug(f'_collect_probas(): Caught exception: {e}')

            # Attempt to regularize explicitly the decision scores
            # Get them either from clf.decision_scores_ or with clf.decision_function()
            if not done:
                if use_decision_scores:
                    logger.debug(f'Voting {self.voting}: collecting decision_scores_ for: {method_obj}')
                    decision_scores = method_obj.decision_scores_.reshape(-1, 1)  # Make sure to reshape(-1,1)
                else:
                    logger.debug(f'Voting {self.voting}: decision_function(): {method_obj}')
                    #decision_scores = method_obj.decision_function(X).reshape(-1, 1)
                    decision_scores = cached_decision_function(obj=method_obj, X=Xscaled).reshape(-1, 1)

                # 'raw' => provide raw scores, without transformation
                if normalization == 'raw':
                    probas_pred = decision_scores
                else:
                    # Regularize scores
                    if normalization == 'linear':
                        normalizer = normalizers['linear']
                    elif normalization == 'unify' or normalization == 'gaussian':
                        normalizer = normalizers['unify']
                    elif normalization == 'standard':
                        normalizer = normalizers['standard']
                    else:
                        raise ValueError(f'Unknown normalization method {normalization}')
                    probas_pred = normalizer.transform(decision_scores)

                # Make into a two-column array (even for raw scores)
                probas_pred = np.hstack((1-probas_pred, probas_pred))

                done = True

            if done:
                probas.append(probas_pred)

        return np.asarray(probas, dtype="float32")

    def _check_voting(self):
        if self.voting == "hard":
            raise AttributeError(
                f"predict_proba is not available when voting={repr(self.voting)}"
            )
        return True

    def _predict(self, X):
        """Collect labels predicted by each underlying estimator.

        Results are always in the same order as estimators.
        """
        y = []
        for method in self.estimators:
            logger.debug(f'Voting {self.voting}: predict(): {method}')

            # Scale
            Xscaled = self.scale_for_estimator(X, method[0])

            #y_pred = method[1].predict(X)
            y_pred = cached_predict(obj=method[1], X=Xscaled)
            if y_pred.ndim > 1:  # saved tf autoencoders
                _, y_pred, _ = self.__fix_saved_tf_scores(X, method)  # This scales internally
            y.append(y_pred)
        return np.asarray(y, dtype="int").T

    @available_if(_check_voting)
    def predict_proba(self, X, normalization=None, combine=None,
                      use_decision_scores=False):
        """Compute probabilities of possible outcomes for samples in X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The input samples.
        normalization: str
            How to transform the individual scores of each estimator. Passed to _collect_probas() internally.
        combine: str
            How to combine the transformed scores of each estimator
            'average' (or None), 'maximization', 'median', 'aom', 'mao', 'no'
            If 'no', a list of underlying probas for each estimator is returned, without any combination.
            The estimator order is the same as in initialization.

        Returns
        -------
        avg : array-like of shape (n_samples, n_classes)
            Weighted average probability for each class per sample.
        """

        # Set default combination method to 'average', if not provided
        combine = combine if combine is not None else self.combine

        check_is_fitted(self)

        # Collect transformed scores (i.e. normalized) from all estimators
        scores_norm = self._collect_probas(X, normalization=normalization, use_decision_scores=use_decision_scores)

        # If we don't combine the scores, just return now
        if combine == 'no':
            proba = scores_norm

        else:
            # Keep only the outlier scores (for class 1), since this is what pyod combiners expect
            scores_norm = np.array([proba[:,1] for proba in scores_norm]).T
            # shape is (n_samples, n_estimators)

            if np.any(np.isnan(scores_norm)):
                raise ValueError("Score is nan!")

            # Combine the scores
            if combine == "average":
                proba = average(scores_norm, estimator_weights=self._weights_not_none)
            elif combine == "maximization":
                proba = maximization(scores_norm)
            elif combine == "median":
                proba = median(scores_norm)
            elif combine == "aom":
                proba = aom(scores_norm, int(len(self.estimators_) / 2))
            elif combine == "moa":
                proba = moa(scores_norm, int(len(self.estimators_) / 2))

            # Add the first column, so the return has two columns like the normal predict_proba()'s
            proba = np.stack((1-proba, proba)).T

        return proba

    def transform(self, X, voting=None, normalization=None, flatten_transform=None):
        """Return class labels or probabilities for X for each estimator.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Training vectors, where `n_samples` is the number of samples and
            `n_features` is the number of features.

        Returns
        -------
        probabilities_or_labels
            If `voting='soft'` and `flatten_transform=True`:
                returns ndarray of shape (n_samples, n_classifiers *
                n_classes), being class probabilities calculated by each
                classifier.
            If `voting='soft' and `flatten_transform=False`:
                ndarray of shape (n_classifiers, n_samples, n_classes)
            If `voting='hard'`:
                ndarray of shape (n_samples, n_classifiers), being
                class labels predicted by each classifier.
        """

        # Use provided arguments, or fallback to initialization values
        voting = voting if voting is not None else self.voting
        flatten_transform = flatten_transform if flatten_transform is not None else self.flatten_transform

        check_is_fitted(self)

        if voting == "soft":
            probas = self._collect_probas(X, normalization=normalization)
            if not self.flatten_transform:
                return probas
            return np.hstack(probas)

        else:
            return self._predict(X)

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
            X = self.scalers[estimator_name].transform(X)
            logger.debug(f"Scaling with {self.scalers[estimator_name].__class__.__name__}, estimator {estimator_name}, data shape {X.shape}")
        else:
            logger.debug(f"No scaling done, estimator {estimator_name}, data shape {X.shape}")

        return X


#=======================
# Caching mechanism (memoization)
# Provide memoized versions of predict(), predict_proba() and decision_function(), based on joblib
#=======================

# Decorators to turn exceptions into outputs and re-raise later

def wrap_exception(func, excclass=Exception):
    """Decorator around to catch a possible Exception and return it as an output

    Given a function func() which returns `output`,
    the decorated function wrap_exception(func) will return a tuple (output, exception):
    - either (output, None) if no exception was caught
    - either (None, exception) if exc `exception` was caught

    Args:
        func (__type__): Wrapped function
        excclass (class): Exception class to catch
    """
    def wrapper(*args, **kwargs):
        try:
            output = func(*args, **kwargs)
        except excclass as e:
            return None, e
        return output, None

    return wrapper

def unwrap_exception(func):
    """Decorator to raise an exception-turned-output by wrap_exception()

    Given a function func() which returns (output, exception), unwrap_exception will either
    - return output, if exception is None
    - raise `exception`, if is not None

    Args:
        func (__type__): Wrapped function, as returned by `wrap_exception` decorator
    """
    def wrapper(*args, **kwargs):
        output, exception = func(*args, **kwargs)

        if exception is None:
            return output
        else:
            raise exception

    return wrapper


# Function versions of the methods predict(), predict_proba(), decision_function()
#       _function_clf_predict()
#       _function_clf_predict_proba()
#       _function_clf_decision_function()

def _function_clf_predict(obj, X, idobj=None, **kwargs):
    """Calls obj.predict(X, **kwargs), catches any exception, and returns (output, exception)

    Accepts an optional `idobj` argument which can be used for caching instead of the `obj` object.
    `idobj` should be an unique identifier alternative of the object `obj`, e.g. like the set of weights for a Keras model.
    The `idobj` is not used internally, but is stored by the caching decorator which memoizes the function.
    To cache an unpickable object like a Keras model, we pass the weights as `idobj`, and cache `idobj` instead of `obj`

    Args:
        obj (_type_): Object
        X (_type_): Data to call predict() on
        idobj (_type_, optional): Alternative unique for `obj`, used for caching. Defaults to None.

    Returns:
        Result of obj.predict(X, **kwargs)
    """

    logger.debug(f"Using cached predict() with id: {idobj}")
    return wrap_exception(obj.predict)(X, **kwargs)

def _function_clf_predict_proba(obj, X, idobj=None, **kwargs):
    """Calls obj.predict_proba(X, **kwargs), catches any exception, and returns (output, exception)

    Accepts an optional `idobj` argument which can be used for caching instead of the `obj` object.
    `idobj` should be an unique identifier alternative of the object `obj`, e.g. like the set of weights for a Keras model.
    The `idobj` is not used internally, but is stored by the caching decorator which memoizes the function.
    To cache an unpickable object like a Keras model, we pass the weights as `idobj`, and cache `idobj` instead of `obj`

    Args:
        obj (_type_): Object
        X (_type_): Data to call predict() on
        idobj (_type_, optional): Alternative unique for `obj`, used for caching. Defaults to None.

    Returns:
        Result of obj.predict_proba(X, **kwargs)
    """

    logger.debug(f"Using cached predict_proba() with id: {idobj}")
    return wrap_exception(obj.predict_proba)(X, **kwargs)

def _function_clf_decision_function(obj=None, X=None, idobj=None, **kwargs):
    """Calls obj.decision_function(X, **kwargs), catches any exception, and returns (output, exception)

    Accepts an optional `idobj` argument which can be used for caching instead of the `obj` object.
    `idobj` should be an unique identifier alternative of the object `obj`, e.g. like the set of weights for a Keras model.
    The `idobj` is not used internally, but is stored by the caching decorator which memoizes the function.
    To cache an unpickable object like a Keras model, we pass the weights as `idobj`, and cache `idobj` instead of `obj`

    Args:
        obj (_type_): Object
        X (_type_): Data to call predict() on
        idobj (_type_, optional): Alternative unique for `obj`, used for caching. Defaults to None.

    Returns:
        Result of obj.decision_function(X, **kwargs)
    """

    logger.debug(f"Using cached decision_function() with id: {idobj}")
    return wrap_exception(obj.decision_function)(X, **kwargs)


# Decorator to log a cache hit or miss

def log_cache_hit(func, logger, funcname='function'):
    """Decorator around a joblib cached function to log a cache hit or miss.

    Args:
        func (__type__): A joblib cached function returned by joblib.Memory.cache()
        logger (Logger): A logger object
        funcname (str, optional): Optional name of the function used for logging. Defaults to 'function'.
    """
    def wrapper(*args, **kwargs):
        cache_message = 'Cache hit' if func.check_call_in_cache(*args, **kwargs) else 'Cache new'
        logger.debug(cache_message + f' when calling cached {funcname}, arguments: {args}; {kwargs}' )

        return func(*args, **kwargs)
    return wrapper


# Internal cached function wrappers
# By default, caching is disabled (location=None)
# `obj` object is always ignored, hashing is actually done on a separate argument `idobj`
# Call set_joblib_cache(location=...) to enable. This will regenerate these handles.

# Chain of decorators:
# - wrap_exception(func) calls func(), catches any exception, and returns (output, exception)
# - this is called by _function_clf_xxx(), as wrap_exception(obj.xxx())
# - this is cached by cache() decorator (caching the tuple (output, exception))
# - log_cache_hit() just prints a cache hit or miss message ahead
# - unwrap_exception() splits (output, exception) and raises back the exception, if any, or returns output

_cached_predict_noobj = unwrap_exception(
                            log_cache_hit(
                                joblib.Memory(location=None).cache(_function_clf_predict, ignore=['obj']),
                                logger, 'predict() (ignore obj)'
                                )
                        )

_cached_predict_proba_noobj =   unwrap_exception(
                                    log_cache_hit(
                                        joblib.Memory(location=None).cache(_function_clf_predict_proba, ignore=['obj']),
                                        logger, 'predict_proba() (ignore obj)'
                                    )
                                )

_cached_decision_function_noobj    =    unwrap_exception(
                                            log_cache_hit(
                                                joblib.Memory(location=None).cache(_function_clf_decision_function, ignore=['obj']),
                                                logger, 'decision_function() (ignore obj)'
                                                )
                                        )

# Top-level cached functions. These are the functions to call from outside
#       cached_predict(obj, X, ...)
#       cached_predict_proba(obj, X, ...)
#       cached_decision_function(obj, X, ...)

def cached_predict(obj, X, **kwargs):
    """Calls obj.predict(X, **kwargs), with caching (memoization).

    TF-based models are cached based on the model weights.
    All other models are cached based on their params, as returned by get_params().

    Args:
        obj (_type_): Object
        X (_type_): Input data

    Returns:
        _type_: Return value of obj.predict(X, **kargs)
    """

    logger.debug(f"Inside cached_predict(), object type: {type(obj)}")

    # Decide what uniquely identifying traits to be used for caching. Whole objects might not be pickable (e.g. tensorflow)
    if isinstance(obj, Autoencoder) or isinstance(obj, VAE):
        idobj=(obj.__class__, obj.get_weights())
    else:
        idobj = (obj.__class__, obj.get_params())

    return _cached_predict_noobj(obj, X, idobj=idobj, **kwargs)

def cached_predict_proba(obj, X, **kwargs):
    """Calls obj.predict_proba(X, **kwargs), with caching (memoization).

    TF-based models are cached based on the model weights.
    All other models are cached based on their params, as returned by get_params().

    Args:
        obj (_type_): Object
        X (_type_): Input data

    Returns:
        _type_: Return value of obj.predict_proba(X, **kargs)
    """

    logger.debug(f"Inside cached_predict_proba(), object type: {type(obj)}")

    # Decide what uniquely identifying traits to be used for caching. Whole objects might not be pickable (e.g. tensorflow)
    if isinstance(obj, Autoencoder) or isinstance(obj, VAE):
        idobj=(obj.__class__, obj.get_weights())
    else:
        idobj = (obj.__class__, obj.get_params())

    return _cached_predict_proba_noobj(obj, X, idobj=idobj, **kwargs)

def cached_decision_function(obj, X, **kwargs):
    """Calls obj.decision_function(X, **kwargs), with caching (memoization).

    TF-based models are cached based on (class, model weights).
    All other models are cached based on (class, params), params being returned by get_params().

    Args:
        obj (_type_): Object
        X (_type_): Input data

    Returns:
        _type_: Return value of obj.decision_function(X, **kargs)
    """

    logger.debug(f"Inside cached_decision_function(), object type: {type(obj)}")

    # Decide what uniquely identifying traits to be used for caching. Whole objects might not be pickable (e.g. tensorflow)
    if isinstance(obj, Autoencoder) or isinstance(obj, VAE):
        idobj=(obj.__class__, obj.get_weights())
    else:
        idobj = (obj.__class__, obj.get_params())
    return _cached_decision_function_noobj(obj, X, idobj=idobj, **kwargs)


def set_joblib_cache(**kwargs):
    """Enable/disable caching of results (memoization) and set caching parameters.

    Passes all the arguments to joblib.Memory()

    Use `set_joblib_cache(location=None) to disable caching. Pass an actual path to enable caching.

        Parameters
        ----------
        location: str, pathlib.Path or None
            The path of the base directory to use as a data store
            or None. If None is given, no caching is done and
            the Memory object is completely transparent. This option
            replaces cachedir since version 0.12.

        backend: str, optional
            Type of store backend for reading/writing cache files.
            Default: 'local'.
            The 'local' backend is using regular filesystem operations to
            manipulate data (open, mv, etc) in the backend.

        cachedir: str or None, optional

            .. deprecated: 0.12
                'cachedir' has been deprecated in 0.12 and will be
                removed in 0.14. Use the 'location' parameter instead.

        mmap_mode: {None, 'r+', 'r', 'w+', 'c'}, optional
            The memmapping mode used when loading from cache
            numpy arrays. See numpy.load for the meaning of the
            arguments.

        compress: boolean, or integer, optional
            Whether to zip the stored data on disk. If an integer is
            given, it should be between 1 and 9, and sets the amount
            of compression. Note that compressed arrays cannot be
            read by memmapping.

        verbose: int, optional
            Verbosity flag, controls the debug messages that are issued
            as functions are evaluated.

        bytes_limit: int, optional
            Limit in bytes of the size of the cache. By default, the size of
            the cache is unlimited. When reducing the size of the cache,
            ``joblib`` keeps the most recently accessed items first.

            **Note:** You need to call :meth:`joblib.Memory.reduce_size` to
            actually reduce the cache size to be less than ``bytes_limit``.

        backend_options: dict, optional
            Contains a dictionnary of named parameters used to configure
            the store backend.

    """
    # Access the module function handles
    global _cached_predict_noobj
    global _cached_predict_proba_noobj
    global _cached_decision_function_noobj

    # Recreate cached function handles, with new joblib arguments
    _cached_predict_noobj = unwrap_exception(
                                log_cache_hit(
                                    joblib.Memory(**kwargs).cache(_function_clf_predict, ignore=['obj']),
                                    logger, 'predict() (ignore obj)'
                                    )
                            )

    _cached_predict_proba_noobj =   unwrap_exception(
                                        log_cache_hit(
                                            joblib.Memory(**kwargs).cache(_function_clf_predict_proba, ignore=['obj']),
                                            logger, 'predict_proba() (ignore obj)'
                                        )
                                    )

    _cached_decision_function_noobj    =    unwrap_exception(
                                                log_cache_hit(
                                                    joblib.Memory(**kwargs).cache(_function_clf_decision_function, ignore=['obj']),
                                                    logger, 'decision_function() (ignore obj)'
                                                    )
                                            )
    logger.info(f"Set joblib cache parameters to {kwargs['location']}")

#=======================
