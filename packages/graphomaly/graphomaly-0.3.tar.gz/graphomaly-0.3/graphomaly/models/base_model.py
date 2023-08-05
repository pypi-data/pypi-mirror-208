# Copyright (c) 2020 Andrei Anton <andrei.anton@tremend.com>, Tremend Software Consulting
# Copyright (c) 2020 Stefania Budulan <stefania.budulan@tremend.com>, Tremend Software Consulting

from abc import ABC
from typing import Any


class BaseModel(ABC):
    """
    Common general interface for models and stateful/tunable algorithms.

    This provides:
    - and sklearn style interface with `fit`, `predict` and/or `fit_predict`
    - a function-like interface where you just call the model like a function
      on the input and get the output ("Keras style"), allowing simple usage
      of transformation algorithms and unsupervides ones
    - optional extra functionality for on-demand (and only once per *class*
      usage) loading of needed modules (optional dependencies)
    """

    _is_fit_predict_implemented: bool
    _are_fit_and_predict_implemented: bool
    _is_load_module_implemented: bool

    _module = None

    def __init__(self, *args, **kwargs):
        self._is_fit_predict_implemented = (
            self.__class__.fit_predict is not BaseModel.fit_predict
        )
        self._are_fit_and_predict_implemented = (
            self.__class__.fit is not BaseModel.fit
            and self.__class__.predict is not BaseModel.predict
        )
        assert (
            self._is_fit_predict_implemented or self._are_fit_and_predict_implemented
        ), "Subclasses of BaseClass mult implement either `fit` and `predict`, or `fit_predict`"

        self._is_load_module_implemented = (
            self.__class__._load_module is not BaseModel._load_module
        )
        if self._is_load_module_implemented and not self._module:
            self._load_module()

    def fit(self, X: Any, y=None, **kwargs) -> "BaseModel":
        ...

    def predict(self, X: Any, **kwargs) -> Any:
        ...

    def fit_predict(self, X: Any, *args, **kwargs) -> Any:
        self.fit(X, *args, **kwargs)
        return self.predict(X, **kwargs)

    def __call__(self, X: Any, *args, **kwargs) -> Any:
        if self._is_fit_predict_implemented:
            return self.fit_predict(X, *args, **kwargs)
        else:
            self.fit(X, *args, **kwargs)
            return self.predict(X, **kwargs)

    @classmethod
    def _load_module(cls):
        """
        Implement this if you need a module to be loaded on demand (optional dependency)

        NOTE: By setting `_module` attribute here instead of just returning it
            and setting in constructor, we get more tools-friendly code.

        Returns
        -------
        module
        """
        # EXAMPLE:
        # import leidenalg as m  # noqa
        # cls._module = m
        ...
