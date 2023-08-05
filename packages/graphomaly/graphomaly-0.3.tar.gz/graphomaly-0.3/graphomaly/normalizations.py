"""normalizations.py

Contains regularization and normalization methods for estimators' scores.
"""


import numpy as np
import math as mt

import sklearn
import scipy.special


#====================================================================
# Regularization methods
# Final scores are in range [0, Inf), larger means more outlying
#===================================================================

## Baseline regularization
def baseline_reg(S,base):
    R = np.maximum(0,S-base)
    return R

## Linear inverse regularization
def lininv_reg(S,Smax):
    R = Smax - S
    return R

## Logarithmic inverse regularization
def loginv_reg(S,Smax):
    R = np.log(Smax) - np.log(S)
    return R


# Class definitions of the transformations, in scikit-learn style. 
# Used StandardScaler as an inspiration
class RegBaseline(sklearn.base.OneToOneFeatureMixin, sklearn.base.TransformerMixin, sklearn.base.BaseEstimator):

    def __init__(self, base = None):
        self.base = base

    def fit(self, X, y=None):
        self.base = np.amin(X, axis=1)  # Assume shape = (n_features, n_observations)

    def transform(self, X):
        return np.maximum(0, X-self.base)

class RegLinInversion(sklearn.base.OneToOneFeatureMixin, sklearn.base.TransformerMixin, sklearn.base.BaseEstimator):

    def __init__(self, Smax = None):
        self.Smax = Smax

    def fit(self, X, y=None):
        self.Smax = np.amax(X, axis=1)  # Assume shape = (n_features, n_observations)

    def transform(self, X):
        return self.Smax-X

class RegLogInversion(sklearn.base.OneToOneFeatureMixin, sklearn.base.TransformerMixin, sklearn.base.BaseEstimator):

    def __init__(self, Smax = None):
        self.Smax = Smax

    def fit(self, X, y=None):
        self.Smax = np.amax(X, axis=1)  # Assume shape = (n_features, n_observations)

    def transform(self, X):
        return np.log(self.Smax / X)


#====================================================================
# Normalizations methods
# Final scores are in range [0, 1], larger means more outlier
#===================================================================

## Simple scaling of scores S into [0,1] values
def Simple_Norm(S,Smin,Smax):
    N = (S - Smin) / (Smax - Smin)
    return N

# Gaussian normalization
def GaussNormalization(S):
    d,N = S.shape
    NormS = np.zeros((d,N))
    for i in range(N):  # loop over detectors
        scores_mean = np.mean(S[:,i])
        scores_dev = np.sqrt(np.var(S[:,i]))   #np.sqrt(np.mean(S[:,i]**2) - (scores_means[i]**2))
        for j in range(d):  # loop over data
            NormS[j,i] = np.maximum(0,mt.erf((S[j,i] - scores_mean) / (np.sqrt(2) * scores_dev)))
    return NormS


# Offer other transformers from scikit-learn, for completitude
import sklearn.preprocessing
MaxAbsScaler   = sklearn.preprocessing.MaxAbsScaler    # Scale by maximum absolute value
MinMaxScaler   = sklearn.preprocessing.MinMaxScaler    # Scale to any [min, max] range, e.g. [0,1]
RobustScaler   = sklearn.preprocessing.RobustScaler    # Subtract the median and scale by quantile range (25th quantile - 75th quantile)
StandardScaler = sklearn.preprocessing.StandardScaler  # Normalize mean and variance, e.g. z = (x - mean)/stddev
QuantileTransformer = sklearn.preprocessing.QuantileTransformer   # Transform each value according to its quantile (a.k.a. histogram equalization to uniform)
PowerTransformer    = sklearn.preprocessing.PowerTransformer      # Transform histogram to Gaussian (a.k.a. histogram equalization to gaussian)

# Class definitions of the transformations, in scikit-learn style. 
# Used StandardScaler as an inspiration
# Naming rule as in sklearn:
# - scaler = linear (affine) transformations
# - transformer = non-linear transformations

class GaussScalingTransformer(sklearn.base.OneToOneFeatureMixin, sklearn.base.TransformerMixin, sklearn.base.BaseEstimator):

    def __init__(self, means = None, devs = None):
        self.means = means
        self.devs  = devs

    def fit(self, X, y=None):
        """Compute and save mean and variance of X

        Args:
            X (_type_): Input data, size (n_features, n_observations)
            y (_type_, optional): Unused
        """
        self.means = np.mean(X, axis=0)  # Assume shape = (n_observations, n_features)
        self.devs  = np.std(X, axis=0)   # Biased or unbiased? Divide by N or by N-1? 

        # If any deviation is 0, raise an error rather than going on
        if any(self.devs == 0):
            raise ValueError("A standard deviation is 0, can't normalize")

        # Must return self 
        return self

    def transform(self, X):
        # Could also use a StandardScaler internally instead of self.means and self.devs
        return np.maximum(0, scipy.special.erf( (X - self.means)/(self.devs * mt.sqrt(2)) ) )