# Copyright (c) 2021 Alexandra Bodirlau <alexandra.bodirlau@tremend.com>, Tremend Software Consulting
# Copyright (c) 2021 Stefania Budulan <stefania.budulan@tremend.com>, Tremend Software Consulting
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

import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import activations, layers
from tensorflow.keras.regularizers import L2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


@tf.keras.utils.register_keras_serializable()
class Autoencoder(tf.keras.Model):
    """Autoencoder model introduced by Aggarwal C. [Aggarwal2015]_

    Parameters
    ----------
    encoder_neurons : list
        The number of neurons per encoder layers.
        Values > 1 are absolute, values <= 1 are relative to input size (e.g. [0.8, 0.4])

    decoder_neurons : list
        The number of neurons per decoder layers.
        Values > 1 are absolute, values <= 1 are relative to input size (e.g. [0.8, 0.4])

    activation_function : str or callable, default='tanh'
        The activation function for all layers.
        See `Keras doc <https://keras.io/api/layers/activations/>`__.

    l2_regularizer : float in (0., 1), default=0.1
        The regularization factor for L2 regularizer for all layers.

    dropout : float in (0., 1), default=0.2
        Dropout rate for all hidden layers.

    threshold : float, default=None
        The threshold used for anomalies selection. If None, the
        contamination is used to compute the threshold.

    contamination : float, default=0.1
        The contamination rate used for computing the reconstruction error
        threshold. Used if threshold is not set.

    optimizer: str or callable, default='adam'
        The optimizer algorithm of the neural network.
        See `Keras doc <https://keras.io/api/optimizers/>`__.

    loss: str or callable, default='mse'
        The loss function of the neural network.
        See `Keras doc <https://keras.io/api/losses/>`__.

    epochs: int, default=1000
        Maximum number of epochs for network training.
        See arguments of fit() method in `Keras doc <https://keras.io/api/models/model_training_apis/>`__.

    batch_size: int, default=10000
        Batch size used for training.
        See arguments of fit() method in `Keras doc <https://keras.io/api/models/model_training_apis/>`__.

    shuffle: boolean, default=True
        Shuffle data before each epoch during training.
        See arguments of fit() method in `Keras doc <https://keras.io/api/models/model_training_apis/>`__.

    validation_size: float, default==0.1
        Amount of training set used for validation.
        See `validation_split` argument of fit() method in `Keras doc <https://keras.io/api/models/model_training_apis/>`__.

    learning_rate : float, default==0.001
        Gradient step size used in training.
        Depends on the optimizer used.

    verbose: int or str, default='auto'
        Print training progress. Can be 0, 1, or 'auto'
        See arguments of fit() method in `Keras doc <https://keras.io/api/models/model_training_apis/>`__.

    es_monitor: str or None, default='val_loss'
        Quantity to monitor for early stopping of training.
        Use None to disable EarlyStopping.
        See `Keras doc <https://keras.io/api/callbacks/early_stopping/>`__.

    es_patience: int, default=50
        Early Stopping: how many epochs to wait before stop.
        See `Keras doc <https://keras.io/api/callbacks/early_stopping/>`__.

    redlr_monitor: str or None, default='val_loss'
        Quantity to monitor for "Reduce Learning Rate on Plateau" during training.
        Use None to disable ReduceLROnPlateau.
        See `Keras doc <https://keras.io/api/callbacks/reduce_lr_on_plateau/>`__.

    redlr_learning_rate_reduce_factor: float, default=0.2
        Factor for reducing learning rate when plateau is detected. Must be < 1.
        Use None to disable ReduceLROnPlateau.
        See `Keras doc <https://keras.io/api/callbacks/reduce_lr_on_plateau/>`__.

    redlr_learning_rate_min: float, default=0.00001
        Minimum learning rate allowed when reducing learning rate on plateau.
        See `Keras doc <https://keras.io/api/callbacks/reduce_lr_on_plateau/>`__.

    redlr_patience: int, default=10
        How many epochs to wait before reducing learning rate on plateau.
        See `Keras doc <https://keras.io/api/callbacks/reduce_lr_on_plateau/>`__.

    savename_key_len: int, default=3
        When saving the model, restrict key length in the name to this many characters.

    Attributes
    ----------
    decision_scores_ : array-like of shape (n_samples,)
        The raw outlier scores for the training data, i.e. the reconstruction errors.
        The anomalies have a larger error score.

    history_ : Keras Object
        The training history of the model.

    labels_ : list of int (0 or 1)
        The binary labels for the training data. 0 means inliers and 1 means
        outliers.

    threshold_ : float
        The threshold for the raw outliers scores.

    encoder_neurons_ : list
        The actual number of neurons per encoder layers, if decoder_neurons is relative

    decoder_neurons_ : list
        The actual number of neurons per decoder layers, if decoder_neurons is relative

    References
    ----------
    .. [Aggarwal2015] Aggarwal C. (2015) Outlier Analysis. In: Data Mining. Springer,
        Cham. https://doi.org/10.1007/978-3-319-14142-8_8
    """

    def __init__(
        self,
        encoder_neurons = None,
        decoder_neurons = None,
        activation_function = "relu",
        l2_regularizer = 0.1,
        dropout = 0.5,
        threshold = None,
        contamination = 0.1,
        optimizer = 'adam',
        loss = "mse",
        epochs = 1000,
        batch_size = 10000,
        shuffle = True,
        validation_size = 0.1,
        learning_rate = 0.001,
        verbose = 1,
        es_monitor = 'val_loss',                       # What to monitor. Required. Comment-out to disable EarlyStopping
        es_patience = 50,                              # How many epochs to wait before stop. Defaults to 0.
        redlr_monitor = 'val_loss',                    # What to monitor. Required. Comment-out to disable ReduceLROnPlateau
        redlr_learning_rate_reduce_factor = 0.2,       # Reduce factor. Must be < 1. Required. Comment-out to disable ReduceLROnPlateau
        redlr_learning_rate_min = 0.00001,             # Minimum learning rate. Defaults to 0.
        redlr_patience = 10,                           # How many epochs to wait before reducing. Defaults to 10.
        savename_key_len = 3                           # When saving, restrict key length in the name to this many characters
    ):
        super(Autoencoder, self).__init__()

        # Fixed parameters, passed via __init__()
        self.encoder_neurons = encoder_neurons
        self.decoder_neurons = decoder_neurons
        self.activation_function = activation_function
        self.l2_regularizer = l2_regularizer
        self.dropout = dropout
        self.threshold = threshold              # Fixed threshold parameter specified at instantiation, while threshold_ is the actual threshold to use
        self.contamination = contamination
        self.optimizer = optimizer
        self.loss = loss
        self.epochs = epochs
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.validation_size = validation_size
        self.learning_rate = learning_rate
        self.verbose = verbose
        self.es_monitor = es_monitor
        self.es_patience = es_patience
        self.redlr_monitor = redlr_monitor
        self.redlr_learning_rate_reduce_factor = redlr_learning_rate_reduce_factor
        self.redlr_learning_rate_min = redlr_learning_rate_min
        self.redlr_patience = redlr_patience
        self.savename_key_len = savename_key_len

        # Fixed parameters, internal
        self.classes = 2

        # Attributes estimated from data, ending with `_`
        # See here for a general discussion: https://scikit-learn.org/stable/developers/develop.html
        self.threshold_ = None                  # Threshold set based on contamination level, if self.threshold is None, else equal to threshold.
        self.decision_scores_ = None
        self.history_ = None
        self.labels_ = None
        self.encoder_neurons_ = None    # Actual layer sizes, if case encoder_neurons contains relative values
        self.decoder_neurons_ = None    # Actual layer sizes, if case decoder_neurons contains relative values

        # sk-learn: nothing should be done in constructor, not even validation
        # validation and building the Keras model is done in fit(), after set_params()

    # See here: https://www.tensorflow.org/api_docs/python/tf/keras/utils/register_keras_serializable
    # "To be serialized and deserialized, classes must implement the get_config() method."
    def get_config(self):
        """Returns all data members of the object, i.e. both the parameters and the attributes (ending in `_`)

        Needed for serialization / deserialization.
        """
        # Get object attributes
        attributes = {  "classes": self.classes,
                        "threshold_": self.threshold_,
                        "decision_scores_": self.decision_scores_,
                        "history_": self.history_,
                        "labels_": self.labels_
            }

        # Join the parameters with the attributes in a single dict
        params = self.get_params()
        params.update(attributes)
        return params

    @classmethod
    def from_config(cls, config):
        """Instantiates an object based on a config dict returned by get_config()
        """

        # Extract attributes from `config` and set later, they cannot be passed to __init__()
        attrs = ["classes", "threshold_", "decision_scores_", "history_", "labels_"]
        attrs_dict = {attr: config.pop(attr) for attr in attrs}

        # Instantiate with the remaining keys
        instance = cls(**config)

        # Set attributes
        for attr, value in attrs_dict.items():
            setattr(instance, attr, value)

        return instance

    def _build_model(self):

        encoder_layers = []

        for neurons in self.encoder_neurons_:
            linear_layer = layers.Dense(
                neurons,
                activation=self.activation_function,
                activity_regularizer=L2(self.l2_regularizer),
            )
            dropout_layer = layers.Dropout(self.dropout)

            encoder_layers.append(linear_layer)
            encoder_layers.append(dropout_layer)

        decoder_layers = []
        for ilayer, neurons in enumerate(self.decoder_neurons_):

            # The last layer should have no activation function
            activation = self.activation_function
            if ilayer == len(self.decoder_neurons_)-1:
                activation = 'linear'

            linear_layer = layers.Dense(
                neurons,
                activation=activation,
                activity_regularizer=L2(self.l2_regularizer),
            )
            dropout_layer = layers.Dropout(self.dropout)

            decoder_layers.append(linear_layer)
            decoder_layers.append(dropout_layer)

        self.encoder = tf.keras.Sequential(encoder_layers, name="encoder")
        self.decoder = tf.keras.Sequential(decoder_layers[:-1], name="decoder")

    def call(self, inputs):
        """Runs the model on the input data.
        """
        if inputs.shape[1] != self.decoder_neurons_[-1]:
            raise ValueError(
                "Expected the number of features to be equal to "
                "the number of neurons on the last decoder layer. "
                f"But found: {inputs.shape[1]} features and "
                f"{self.decoder_neurons_[-1]} neurons."
            )

        encoded = self.encoder(inputs)
        decoded = self.decoder(encoded)

        return decoded

    def summary(self):
        """Print Autoencoder architecture on components."""
        print(self.encoder.summary())
        print(self.decoder.summary())

    def decision_function(self, X):
        """Compute the reconstruction errors for some samples.
        The anomalies have a larger error score.

        This does not modify the object. Use for prediction, not fitting.

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the scores.

        Returns
        -------
        ndarray of shape (num_samples, )
            The reconstruction error scores.
        """
        preds = super().predict(X)
        return Autoencoder._compute_scores(X, preds)

    def predict_proba(self, X=None, method="linear", thresh=None):
        """Compute a distribution probability on the reconstuction errors
        predicted for the samples passed as parameter.

        This does not modify the object. Use for prediction, not fitting.

        If X is not None, the errors are computed for the data in X
        If X is None, assume the erorrs are already available in `self.decision_scores_`

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the probabilities.

        method : {'linear', 'hard', 'quantile'}, default='linear'
                 The method used for score normalization. Possible values:

                 - 'linear': scale scores to [0, 1] range. Default.
                 - 'hard': hard thresholding with a given threshold `thresh`, return binary scores. If `thresh` is None, use `self.threshold_` instead.
                 - 'quantile': hard thresholding using the given quantile in `thresh`,
                   e.g. thresh=0.1 assigns 0 to the smallest 10% errors, and 1 to the largest 90% errors.

        Returns
        -------
        ndarray of shape (num_samples, )
            The probabilities for each class (normal prob on dimension 0,
            anomaly prob on dimension 1).
        """

        # If X is None, we process the error values stored in self.decision_scores_
        if X is None and self.decision_scores_ is None:
            raise Exception(
                "Reconstruction errors on train set are not available."
            )

        rec_errors = self.decision_function(X) if X is not None else self.decision_scores_

        probs = np.zeros([rec_errors.shape[0], self.classes])

        if method == "linear":
            scaler = MinMaxScaler()
            probs[:, 1] = scaler.fit_transform(rec_errors.reshape(-1, 1)).squeeze()
            probs[:, 0] = 1 - probs[:, 1]

        elif method == "hard" and (thresh is not None or self.threshold_ is not None):
            thresh_local = thresh if thresh is not None else self.threshold_   # given threshold, or fitted one
            probs[:, 1] = (rec_errors > thresh_local).astype("int")

        elif method == "quantile" and thresh is not None:
            q_thresh = np.quantile(rec_errors, thresh)
            probs[:, 1] = (rec_errors > q_thresh).astype("int")

        else:
            raise ValueError(
                f"method={method}, thresh={thresh} is not a valid combination for probability conversion."
            )

        return probs

    def set_params(self, **kwargs):
        """Set estimator parameters"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def get_params(self, deep=True):
        """Returns all parameters of the estimator. Needed for Scikit-learn compatibility
        """

        # Don't return the attributes (ending in `_``)
        return {
            "encoder_neurons": self.encoder_neurons,
            "decoder_neurons": self.decoder_neurons,
            "activation_function": self.activation_function,
            "l2_regularizer": self.l2_regularizer,
            "dropout": self.dropout,
            "contamination": self.contamination,
            "threshold": self.threshold,
            "optimizer": self.optimizer,
            "loss": self.loss,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "shuffle": self.shuffle,
            "validation_size": self.validation_size,
            "learning_rate": self.learning_rate,
            "verbose": self.verbose,
            "es_monitor": self.es_monitor,
            "es_patience": self.es_patience,
            "redlr_monitor": self.redlr_monitor,
            "redlr_learning_rate_reduce_factor": self.redlr_learning_rate_reduce_factor,
            "redlr_learning_rate_min": self.redlr_learning_rate_min,
            "redlr_patience": self.redlr_patience,
            "savename_key_len": self.savename_key_len
        }

    def fit(self, X, y=None, **kwargs):
        """Fits the model on the data provided."""

        self.set_params(**kwargs)

        # When the last decoder layer has size 1, the values are relative.
        # Scale the numbers by input size.
        # Note the trailing underscore_!
        input_size = X.shape[1]
        if round(self.decoder_neurons[-1]) == 1:
            self.encoder_neurons_ = [round(v * input_size) for v in self.encoder_neurons]
            self.decoder_neurons_ = [round(v * input_size) for v in self.decoder_neurons]
            logger.info(f'Layer size was relative, actual sizes are: encoder: {self.encoder_neurons_}, decoder: {self.decoder_neurons_}')
        else:
            self.encoder_neurons_ = self.encoder_neurons
            self.decoder_neurons_ = self.decoder_neurons

        self._check_parameters()
        self._build_model()

        self.compile(optimizer=self.optimizer, loss=self.loss)

        # Overwrite learning rate, if specified
        if hasattr(self, 'learning_rate'):
            self.optimizer.learning_rate = self.learning_rate

        # Add callbacks
        # - Early Stopping: stop after a number of epochs not improving, get best model
        callbacks = []
        if hasattr(self, 'es_monitor'):
            es_patience = self.es_patience if hasattr(self, 'es_patience') else 0    # defaults to 0
            callbacks.append(EarlyStopping(monitor=self.es_monitor, patience=es_patience, restore_best_weights=True))

        # - Reduce learning-rate on plateau
        if hasattr(self, 'redlr_monitor') and hasattr(self, 'redlr_learning_rate_reduce_factor'):
            redlr_learning_rate_min = \
                self.redlr_learning_rate_min if hasattr(self, 'redlr_learning_rate_min') else 0    # defaults to 0
            redlr_patience = \
                self.redlr_patience if hasattr(self, 'redlr_patience') else 10   # defaults to 10
            callbacks.append(ReduceLROnPlateau(monitor=self.redlr_monitor, factor=self.redlr_learning_rate_reduce_factor,
                                            patience=redlr_patience, min_lr=redlr_learning_rate_min))

        # Train!
        self.history_ = (
            super()
            .fit(
                X,
                X,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=self.validation_size,
                shuffle=self.shuffle,
                verbose=self.verbose,
                callbacks=callbacks
            )
            .history
        )

        # Fit the threshold, based on the reconstruction errors on the training set
        self.decision_scores_ = self.decision_function(X)
        if self.threshold is None:
            self.threshold_ = np.quantile(self.decision_scores_, 1 - self.contamination)
        else:
            self.threshold_ = self.threshold

        # Compute the labels on the training set
        self.labels_ = self.predict_proba(method='hard', thresh=self.threshold_)[:,1]

        return self

    def predict(self, X):
        """Predict binary labels for the samples passed as parameter.

        This does not modify the object. Use for prediction, not fitting.

        Parameters
        ----------
        X : array-like of shape (num_samples, num_features)
            The samples for which to compute the probabilities.

        Returns
        -------
        ndarray of shape (num_samples, )
            The predicted labels for all input.
        """

        pred_score = self.decision_function(X)
        labels = (pred_score > self.threshold_).astype("int")
        return labels

    def fit_predict(self, X, y=None):
        """Run fit() and the predict()"""
        # Fit already does prediction internally, and the labels are in labels_
        return self.fit(X, y).labels_

    def _check_parameters(self):
        if not isinstance(self.encoder_neurons, list):
            raise TypeError(
                "Expected encoder_neurons to have type list, but "
                f"received {type(self.encoder_neurons)}"
            )

        if not isinstance(self.decoder_neurons, list):
            raise TypeError(
                "Expected decoder_neurons to have type list, but "
                f"received {type(self.encoder_neurons)}"
            )

        if not all(map(lambda x: isinstance(x, int), self.encoder_neurons_)):
            raise TypeError("Not all elements from encoder_neurons_ have int " "type")

        if not all(map(lambda x: isinstance(x, int), self.decoder_neurons_)):
            raise TypeError("Not all elements from decoder_neurons_ have int " "type")

        # Check layers size is not 0
        if any (map(lambda x: x == 0, self.encoder_neurons_)):
            raise ValueError("Some layer size from encoder_neurons_ is 0")

        if any (map(lambda x: x == 0, self.decoder_neurons_)):
            raise ValueError("Some layer size from decoder_neurons_ is 0")

        # Check regularizer type and value
        if not isinstance(self.l2_regularizer, float):
            raise TypeError(
                "Expected l2_regularizer to have type float, but "
                f"received {type(self.l2_regularizer)}"
            )

        if self.l2_regularizer < 0.0 or self.l2_regularizer > 1.0:
            raise ValueError(
                "Expected l2_regularizer to have a value in (0.0,"
                f"1.0) range, but received {self.l2_regularizer}"
            )

        # Check activation_function value and type
        if isinstance(self.activation_function, str):
            try:
                activations.deserialize(str(self.activation_function))
            except ValueError:
                raise ValueError(
                    "activation_function value is not supported. "
                    "Please check: https://keras.io/api/layers/activations/"
                    " for available values."
                )

        elif not isinstance(self.activation_function, callable):
            raise TypeError(
                "Expected activation_function to be str or "
                "callable. Please check: "
                "https://keras.io/api/layers/activations/ for "
                "available values."
            )

        if self.contamination is None and self.threshold is None:
            raise TypeError(
                "Expected 'contamination' or 'threshold' to "
                "be float, but received None."
            )

    @staticmethod
    def _compute_scores(X, Y):
        return np.sqrt(np.sum(np.square(Y - X), axis=1))
