from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Mapping

from .base_model import BaseModel
from .sklearn import SklearnIsolationForest


@dataclass
class ModelConfig:
    module: str
    constructor: str
    defaults: Mapping[str, Any]


# EXAMPLE of 100% PyOD compatible integration of a sklearn-model
# class SklearnIsolationForest(sklearn.ensemble.IsolationForest):
#     def __init__(self, n_estimators=500, **kwargs) -> None:
#         super().__init__(n_estimators=n_estimators, **kwargs)

#     def decision_function(self, X):
#         # flip decision funciton sign to match PyOD convention
#         return -super(SklearnIsolationForest, self).decision_function(X)

#     def predict(self, X):
#         # PyOD uses “0” to represent inliers and “1” to represent outliers.
#         # Differently, scikit-learn returns “-1” for anomalies/outliers and “1” for inliers.
#         # convert outputs from -1 (outlier) / 1 (inlier) to 0 (inlier) / 1 (outlier)
#         return (-1 * super().predict(X) + 1) / 2


class ModelsLoader:
    models = {
        "PyodKNN": ModelConfig(
            module="pyod.models.knn",
            constructor="KNN",
            defaults=dict(
                n_neighbors=4,
                method="largest",
            ),
        ),
        "PyodIForest": ModelConfig(
            module="pyod.models.iforest",
            constructor="IForest",
            defaults={},
        ),
        "PyodCOPOD": ModelConfig(
            module="pyod.models.copod",
            constructor="COPOD",
            defaults={},
        ),
        "PyodSOD": ModelConfig(
            module="pyod.models.sod",
            constructor="SOD",
            defaults=dict(ref_set=3, n_neighbors=6),
        ),
        "PyodSOS": ModelConfig(
            module="pyod.models.sos",
            constructor="SOS",
            defaults=dict(perplexity=4),
        ),
        "PyodLOCI": ModelConfig(
            module="pyod.models.loci",
            constructor="LOCI",
            defaults={},
        ),
        "PyodABOD": ModelConfig(
            module="pyod.models.abod",
            constructor="ABOD",
            defaults={},
        ),
        "PyodLODA": ModelConfig(
            module="pyod.models.loda",
            constructor="LODA",
            defaults={},
        ),
        "PyodMCD": ModelConfig(
            module="pyod.models.mcd",
            constructor="MCD",
            defaults={},
        ),
        "PyodLMDD": ModelConfig(
            module="pyod.models.lmdd",
            constructor="LMDD",
            defaults={},
        ),
        "PyodCOF": ModelConfig(
            module="pyod.models.cof",
            constructor="COF",
            defaults={},
        ),
        "PyodCBLOF": ModelConfig(
            module="pyod.models.cblof",
            constructor="CBLOF",
            defaults={},
        ),
        "PyodLOF": ModelConfig(
            module="pyod.models.lof",
            constructor="LOF",
            defaults={},
        ),
        "PyodHBOS": ModelConfig(
            module="pyod.models.hbos",
            constructor="HBOS",
            defaults={},
        ),
        "PyodOCSVM": ModelConfig(
            module="pyod.models.ocsvm",
            constructor="OCSVM",
            defaults={},
        ),
        "PyodVAE": ModelConfig(
            module="pyod.models.vae",
            constructor="VAE",
            defaults={},
        ),
        "AmlAE": ModelConfig(
            module="graphomaly.models.autoencoder",
            constructor="Autoencoder",
            defaults={
                "encoder_neurons": [32, 16, 8, 4],
                # Last layer must have a number of neurons equal to n_features,
                # otherwise it will be overwritten with n_features resulting
                # from the dataset.
                "decoder_neurons": [8, 16, 32, 52],
                "activation_function": "tanh",
                "dropout": 0.0,
                "l2_regularizer": 0.2,
            },
        ),
        "AmlVAE": ModelConfig(
            module="graphomaly.models.vae",
            constructor="VAE",
            defaults={
                "encoder_neurons": [32, 16, 8, 4],
                # Last layer must have a number of neurons equal to n_features,
                # otherwise it will be overwritten with n_features resulting
                # from the dataset.
                "decoder_neurons": [8, 16, 32, 52],
                "latent_dim": 2,
                # Must be equal to n_features, otherwise it will be overwritten
                # with n_features resulting from the dataset.
                "input_dim": 52,
                "activation_function": "tanh",
                "dropout": 0.0,
                "l2_regularizer": 0.2,
            },
        ),
        "SklearnIsolationForest": SklearnIsolationForest,
        # "SklearnIsolationForest": ModelConfig(
        #     module="sklearn.ensemble",
        #     constructor="IsolationForest",
        #     defaults=dict(
        #         n_estimators=500,
        #     ),
        # ),
        "SklearnOCSVM": ModelConfig(
            module="sklearn.svm",
            constructor="OneClassSVM",
            defaults=dict(
                kernel="sigmoid",
                gamma="scale",
            ),
        ),
        "TodsKDiscord": ModelConfig(
            module="tods.detection_algorithm.core.KDiscord",
            constructor="KDiscord",
            defaults=dict(
                window_size=1,
            ),
        ),
        "TodsMultiAutoRegOD": ModelConfig(
            module="tods.detection_algorithm.core.MultiAutoRegOD",
            constructor="MultiAutoRegOD",
            defaults=dict(
                window_size=1,
            ),
        ),
        "TodsLSTMOutlierDetector": ModelConfig(
            module="tods.detection_algorithm.core.LSTMOD",
            constructor="LSTMOutlierDetector",
            defaults={},
        ),
        "AnomalyDL": ModelConfig(
            module="graphomaly.models.dictlearn",
            constructor="AnomalyDL",
            defaults={},
        ),
    }

    @classmethod
    def get(cls, model: str, **kwargs) -> Callable:
        if isinstance(cls.models[model], ModelConfig):
            if model != "AmlAE" and model != "AmlVAE":
                kwargs.update(cls.models[model].defaults)
            return cls.get_constructor(model)(**kwargs)
        else:
            return cls.get_constructor(model)(**kwargs)

    @classmethod
    def get_constructor(cls, model: str) -> Callable:
        if isinstance(cls.models[model], ModelConfig):
            conf = cls.models[model]
            # load module and get constructor
            m = import_module(conf.module)
            ctor = getattr(m, conf.constructor)
            # ensure model will also be callable as simple function
            if not issubclass(ctor, BaseModel) and not hasattr(ctor, "__call__"):
                ctor.__call__ = BaseModel.__call__
            return ctor
        else:
            return cls.models[model]
