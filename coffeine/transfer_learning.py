import numpy as np
from pyriemann.transfer import TLCenter, TLStretch, encode_domains
from sklearn.base import BaseEstimator, TransformerMixin


def _check_data(X):
    # make proper 3d array of covariances
    out = None
    if X.ndim == 3:
        out = X
    elif X.values.dtype == 'object':
        # first remove unnecessary dimensions,
        # then stack to 3d data
        values = X.values
        if values.shape[1] == 1:
            values = values[:, 0]
        out = np.stack(values)
        if out.ndim == 2:  # deal with single sample
            assert out.shape[0] == out.shape[1]
            out = out[np.newaxis, :, :]
    return out


class ReCenter(BaseEstimator, TransformerMixin):
    """Re-center each dataset seperately for transfer learning.

    The data from each dataset are re-centered to the Identity using TLCenter
    from Pyriemann. The difference is we assume to not have target data in the
    training sample so when the transform function is called we fit_transform
    TLCenter on the target (test) data.

    Parameters
    ----------
    metric : str, default='riemann'
        The metric to compute the mean.
    """
    def __init__(self, domains, metric='riemann'):
        self.domains = domains
        self.metric = metric

    def fit(self, X, y):
        """Fit ReCenter.

        Mean of each domain are calculated with TLCenter from
        pyRiemann.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        self : ReCenter instance
        """
        X = _check_data(X)
        _, y_enc = encode_domains(X, y, self.domains)
        self.re_center_ = TLCenter('target_domain', metric=self.metric)
        self.means_ = self.re_center_.fit(X, y_enc).recenter_
        return self

    def transform(self, X, y=None):
        """Re-center the test data.

        Calculate the mean and then transform the data.
        It is assumed that data points in X are all from the same domain
        and that this domain is not present in the data used in fit.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        X_rct : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices with mean at the Identity.
        """
        X = _check_data(X)
        n_sample = X.shape[0]
        _, y_enc = encode_domains(X, [0]*n_sample, ['target_domain']*n_sample)
        self.re_center_ = TLCenter('target_domain', metric=self.metric)
        X_rct = self.re_center_.fit_transform(X, y_enc)
        return X_rct

    def fit_transform(self, X, y):
        """Fit ReCenter and transform the data.

        Calculate the mean of each domain with TLCenter from pyRiemann and
        then transform the data.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        X_rct : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices with mean at the Identity.
        """
        X = _check_data(X)
        _, y_enc = encode_domains(X, y, self.domains)
        self.re_center_ = TLCenter('target_domain', metric=self.metric)
        X_rct = self.re_center_.fit_transform(X, y_enc)
        return X_rct


class ReScale(BaseEstimator, TransformerMixin):
    """Re-scale each dataset seperately for transfer learning.

    The data from each dataset are re-scaled to the Identity using TLStretch
    from Pyriemann. The difference is we assume to not have target data in the
    training sample so when the transform function is called we fit_transform
    TLStretch on the target (test) data. It is also assumed that the data were
    re-centered beforehand.

    Parameters
    ----------
    metric : str, default='riemann'
        The metric to compute the dispersion.
    """
    def __init__(self, domains, metric='riemann'):
        self.domains = domains
        self.metric = metric

    def fit(self, X, y):
        """Fit ReScale.

        Dispersions around the mean of each domain are calculated with
        TLStretch from pyRiemann.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        self : ReScale instance
        """
        X = _check_data(X)
        _, y_enc = encode_domains(X, y, self.domains)
        self.re_scale_ = TLStretch('target_domain',
                                   centered_data=False,
                                   metric=self.metric)
        self.dispersions_ = self.re_scale_.fit(X, y_enc).dispersions_
        return self

    def transform(self, X, y=None):
        """Re-scale the test data.

        Calculate the dispersion around the mean iand then transform the data.
        It is assumed that data points in X are all from the same domain
        and that this domain is not present in the data used in fit.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        X_str : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices with a dispersion equal to 1.
        """
        X = _check_data(X)
        n_sample = X.shape[0]
        _, y_enc = encode_domains(X, [0]*n_sample, ['target_domain']*n_sample)
        self.re_scale_ = TLStretch('target_domain',
                                   centered_data=False,
                                   metric=self.metric)
        self.re_scale_.fit(X, y_enc)
        X_str = self.re_scale_.transform(X)
        return X_str

    def fit_transform(self, X, y):
        """Fit ReScale and transform the data.

        Calculate the dispersions around the mean of each domain with
        TLStretch from pyRiemann and then transform the data.

        Parameters
        ----------
        X : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices.
        y: ndarray, shape (n_matrices,)
            Labels for each matrix.
        Returns
        -------
        X_str : ndarray, shape (n_matrices, n_channels, n_channels)
            Set of SPD matrices with a dispersion equal to 1.
        """
        X = _check_data(X)
        _, y_enc = encode_domains(X, y, self.domains)
        self.re_scale_ = TLStretch('target_domain',
                                   centered_data=False,
                                   metric=self.metric)
        X_str = self.re_scale_.fit_transform(X, y_enc)
        return X_str