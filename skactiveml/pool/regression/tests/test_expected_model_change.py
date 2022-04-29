import unittest

import numpy as np

from skactiveml.pool.regression import ExpectedModelChange
from skactiveml.pool.regression.tests.test_pool_regression import (
    provide_test_regression_query_strategy_init_random_state,
    provide_test_regression_query_strategy_init_missing_label,
    provide_test_regression_query_strategy_query_X,
    provide_test_regression_query_strategy_query_y,
    provide_test_regression_query_strategy_query_reg,
    provide_test_regression_query_strategy_query_fit_reg,
    provide_test_regression_query_strategy_query_sample_weight,
    provide_test_regression_query_strategy_query_candidates,
    provide_test_regression_query_strategy_query_batch_size,
    provide_test_regression_query_strategy_query_return_utilities,
)
from skactiveml.regressor import NICKernelRegressor


class TestExpectedModelChange(unittest.TestCase):
    def setUp(self):
        self.random_state = 1
        self.candidates = np.array([[8, 1], [9, 1], [5, 1]])
        self.X = np.array([[1, 2], [5, 8], [8, 4], [5, 4]])
        self.y = np.array([0, 1, 2, -2])
        self.reg = NICKernelRegressor()
        self.qs = ExpectedModelChange()
        self.query_kwargs = dict(
            X=self.X, y=self.y, candidates=self.candidates, reg=self.reg
        )

    def test_init_param_random_state(self):
        provide_test_regression_query_strategy_init_random_state(
            self, ExpectedModelChange
        )

    def test_init_param_missing_label(self):
        provide_test_regression_query_strategy_init_missing_label(
            self, ExpectedModelChange
        )

    def test_init_param_k_bootstrap(self):
        for wrong_val, error in zip(["five", 0], [TypeError, ValueError]):
            qs = ExpectedModelChange(k_bootstraps=wrong_val)
            self.assertRaises(error, qs.query, **self.query_kwargs)

    def test_init_param_n_train(self):
        for wrong_val, error in zip(["five", 1.5], [TypeError, ValueError]):
            qs = ExpectedModelChange(n_train=wrong_val)
            self.assertRaises(error, qs.query, **self.query_kwargs)

    def test_init_param_ord(self):
        qs = ExpectedModelChange(ord="wrong_norm")
        self.assertRaises(ValueError, qs.query, **self.query_kwargs)

    def test_query_param_X(self):
        provide_test_regression_query_strategy_query_X(self, ExpectedModelChange)

    def test_query_param_y(self):
        provide_test_regression_query_strategy_query_y(self, ExpectedModelChange)

    def test_query_param_reg(self):
        provide_test_regression_query_strategy_query_reg(self, ExpectedModelChange)

    def test_query_param_fit_reg(self):
        provide_test_regression_query_strategy_query_fit_reg(self, ExpectedModelChange)

    def test_query_param_sample_weight(self):
        provide_test_regression_query_strategy_query_sample_weight(
            self, ExpectedModelChange
        )

    def test_query_param_candidates(self):
        provide_test_regression_query_strategy_query_candidates(
            self, ExpectedModelChange
        )

    def test_query_param_batch_size(self):
        provide_test_regression_query_strategy_query_batch_size(
            self, ExpectedModelChange
        )

    def test_query_param_return_utilities(self):
        provide_test_regression_query_strategy_query_return_utilities(
            self, ExpectedModelChange
        )
