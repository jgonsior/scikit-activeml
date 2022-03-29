from copy import deepcopy

import numpy as np
from sklearn import clone
from sklearn.utils.validation import _is_arraylike, check_random_state

from skactiveml.base import SingleAnnotPoolBasedQueryStrategy, SkactivemlRegressor
from skactiveml.utils import simple_batch, check_type


class QBC(SingleAnnotPoolBasedQueryStrategy):
    """Regression based on Query by Committee

    This class implements an Regression adaption of Query by Committee. It
    tries to estimate the model variance by a Committee of estimators.

    Parameters
    ----------
    random_state: numeric | np.random.RandomState, optional
        Random state for candidate selection.

    References
    ----------
    [1] Burbidge, Robert and Rowland, Jem J and King, Ross D. Active learning
        for regression based on query by committee. International conference on
        intelligent data engineering and automated learning, pages 209--218,
        2007.

    """

    def __init__(self, random_state=None,):
        super().__init__(random_state=random_state)

    def query(self, X, y, ensemble, fit_ensemble=True, sample_weight=None,
              candidates=None, batch_size=1, return_utilities=False):
        """Determines for which candidate samples labels are to be queried.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data set, usually complete, i.e. including the labeled and
            unlabeled samples.
        y : array-like of shape (n_samples)
            Labels of the training data set (possibly including unlabeled ones
            indicated by self.MISSING_LABEL.
        ensemble: {SkactivemlRegressor, array-like}
            Regressor to predict the data.
        fit_ensemble : bool, optional (default=True)
            Defines whether the classifier should be fitted on `X`, `y`, and
            `sample_weight`.
        sample_weight: array-like of shape (n_samples), optional (default=None)
            Weights of training samples in `X`.
        candidates : None or array-like of shape (n_candidates), dtype=int or
            array-like of shape (n_candidates, n_features),
            optional (default=None)
            If candidates is None, the unlabeled samples from (X,y) are
            considered as candidates.
            If candidates is of shape (n_candidates) and of type int,
            candidates is considered as the indices of the samples in (X,y).
            If candidates is of shape (n_candidates, n_features), the
            candidates are directly given in candidates (not necessarily
            contained in X). This is not supported by all query strategies.
        batch_size : int, optional (default=1)
            The number of samples to be selected in one AL cycle.
        return_utilities : bool, optional (default=False)
            If true, also return the utilities based on the query strategy.

        Returns
        -------
        query_indices : numpy.ndarray of shape (batch_size)
            The query_indices indicate for which candidate sample a label is
            to queried, e.g., `query_indices[0]` indicates the first selected
            sample.
            If candidates is None or of shape (n_candidates), the indexing
            refers to samples in X.
            If candidates is of shape (n_candidates, n_features), the indexing
            refers to samples in candidates.
        utilities : numpy.ndarray of shape (batch_size, n_samples) or
            numpy.ndarray of shape (batch_size, n_candidates)
            The utilities of samples after each selected sample of the batch,
            e.g., `utilities[0]` indicates the utilities used for selecting
            the first sample (with index `query_indices[0]`) of the batch.
            Utilities for labeled samples will be set to np.nan.
            If candidates is None or of shape (n_candidates), the indexing
            refers to samples in X.
            If candidates is of shape (n_candidates, n_features), the indexing
            refers to samples in candidates.
        """

        X, y, candidates, batch_size, return_utilities = self._validate_data(
            X, y, candidates, batch_size, return_utilities, reset=True
        )

        if isinstance(ensemble, SkactivemlRegressor) and \
                hasattr(ensemble, 'n_estimators'):

            if fit_ensemble:
                ensemble = clone(ensemble).fit(X, y, sample_weight)

            if hasattr(ensemble, 'estimators_'):
                est_arr = ensemble.estimators_
            else:
                est_arr = [ensemble] * ensemble.n_estimators
        elif _is_arraylike(ensemble):
            est_arr = deepcopy(ensemble)
            for idx, est in enumerate(est_arr):
                check_type(est, f'ensemble[{idx}]', SkactivemlRegressor)
                if fit_ensemble:
                    est_arr[idx] = est.fit(X, y, sample_weight)
        else:
            raise TypeError(
                f'`ensemble` must either be a `{SkactivemlRegressor} '
                f'with the attribute `n_esembles` and `estimators_` after '
                f'fitting or a list of {SkactivemlRegressor} objects.'
            )

        X_cand, mapping = self._transform_candidates(candidates, X, y)

        results = np.array([learner.predict(X_cand) for learner in est_arr])
        utilities_cand = np.std(results, axis=0)

        if mapping is None:
            utilities = utilities_cand
        else:
            utilities = np.full(len(X), np.nan)
            utilities[mapping] = utilities_cand

        return simple_batch(utilities, self.random_state_,
                            batch_size=batch_size,
                            return_utilities=return_utilities)

    # TODO: https://aclanthology.org/D08-1112.pdf




