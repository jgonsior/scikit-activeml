import unittest
from copy import deepcopy

import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier

from skactiveml.classifier import SklearnClassifier, ParzenWindowClassifier
from skactiveml.pool import UncertaintySampling, expected_average_precision
from skactiveml.pool._uncertainty_sampling import uncertainty_scores
from skactiveml.utils import MISSING_LABEL
from skactiveml.tests.template_query_strategy import TemplateSingleAnnotatorPoolQueryStrategy


class TestUncertaintySampling(TemplateSingleAnnotatorPoolQueryStrategy,
                              unittest.TestCase):
    def setUp(self):
        self.classes = [0, 1]
        query_default_params_clf = {
            'X': np.array([[1, 2], [5, 8], [8, 4], [5, 4]]),
            'y': np.array([0, 1, MISSING_LABEL, MISSING_LABEL]),
            'clf': ParzenWindowClassifier(random_state=0, classes=self.classes),
        }
        super().setUp(qs_class=UncertaintySampling, init_default_params={},
                      query_default_params_clf=query_default_params_clf)

    def test_init_param_method(self, test_cases=None):
        test_cases = [] if test_cases is None else test_cases
        test_cases += [(1, TypeError), ("string", ValueError)]
        self._test_param("init", "method", test_cases)

    def test_init_param_cost_matrix(self, test_cases=None):
        test_cases = [] if test_cases is None else test_cases
        test_cases += [(np.ones((2, 3)), ValueError), ("string", ValueError),
                       (np.ones((3, 3)), ValueError)]
        self._test_param("init", "cost_matrix", test_cases)
        self._test_param("init", "cost_matrix",
                         [(np.ones([2, 2]) - np.eye(2), ValueError)],
                         replace_init_params={'method': "entropy"})

    def test_query_param_sample_weight(self, test_cases=None):
        test_cases = [] if test_cases is None else test_cases
        test_cases += [("string", ValueError),
                       (self.query_default_params_clf['X'], ValueError),
                       (np.empty((len(self.X) - 1)), ValueError)]
        self._test_param("query", "sample_weight", test_cases)

    def test_query(self):
        compare_list = []
        clf = SklearnClassifier(
            estimator=GaussianProcessClassifier(),
            random_state=self.init_default_params['random_state'],
            classes=self.classes
        )

        # query
        qs = UncertaintySampling(method="entropy")
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])
        compare_list.append(qs.query(**self.query_default_params_clf))

        qs = UncertaintySampling(method="margin_sampling")
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])
        compare_list.append(qs.query(**self.query_default_params_clf))

        qs = UncertaintySampling(method="least_confident")
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])
        compare_list.append(qs.query(**self.query_default_params_clf))

        for x in compare_list:
            self.assertEqual(compare_list[0], x)

        qs = UncertaintySampling(
            method="margin_sampling", cost_matrix=[[0, 1], [1, 0]]
        )
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])

        qs = UncertaintySampling(
            method="least_confident", cost_matrix=[[0, 1], [1, 0]]
        )
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])

        qs = UncertaintySampling(method="expected_average_precision")
        qs.query(candidates=[[1]], clf=clf, X=[[1]], y=[MISSING_LABEL])

        candidates = np.random.rand(10, 2)
        query_params = deepcopy(self.query_default_params_clf)
        query_params['candidates'] = candidates
        best_indices, utilities = qs.query(
            **query_params, return_utilities=True
        )
        self.assertEqual(utilities.shape, (1, len(candidates)))
        self.assertEqual(best_indices.shape, (1,))


class TestExpectedAveragePrecision(unittest.TestCase):
    def setUp(self):
        self.classes = np.array([0, 1])
        self.probas = np.array([[0.4, 0.6], [0.3, 0.7]])
        self.scores_val = np.array([2.0, 2.0])

    def test_param_classes(self):
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=[],
            probas=self.probas,
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes="string",
            probas=self.probas,
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=[0],
            probas=self.probas,
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=[0, 1, 2],
            probas=self.probas,
        )

    def test_param_probas(self):
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=self.classes,
            probas=[1],
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=self.classes,
            probas=[[[1]]],
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=self.classes,
            probas=[[0.7, 0.1, 0.2]],
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=self.classes,
            probas=[[0.6, 0.2]],
        )
        self.assertRaises(
            ValueError,
            expected_average_precision,
            classes=self.classes,
            probas="string",
        )

    def test_expected_average_precision(self):
        expected_average_precision(classes=self.classes, probas=[[0.0, 1.0]])
        scores = expected_average_precision(
            classes=self.classes, probas=self.probas
        )
        self.assertTrue(scores.shape == (len(self.probas),))
        np.testing.assert_array_equal(scores, self.scores_val)


class TestUncertaintyScores(unittest.TestCase):
    def setUp(self):
        self.probas = np.array([[0.2, 0.5, 0.3], [0.1, 0.7, 0.2]])
        self.classes = np.array([0, 1, 2])
        self.cost_matrix = np.ones((3, 3))

    def test_param_probas(self):
        self.assertRaises(ValueError, uncertainty_scores, probas=[1])
        self.assertRaises(ValueError, uncertainty_scores, probas=[[[1]]])
        self.assertRaises(
            ValueError, uncertainty_scores, probas=[[0.6, 0.1, 0.2]]
        )
        self.assertRaises(ValueError, uncertainty_scores, probas="string")

    def test_init_param_method(self):
        self.assertRaises(
            ValueError, uncertainty_scores, self.probas, method="String"
        )
        self.assertRaises(
            ValueError, uncertainty_scores, self.probas, method=1
        )

    def test_param_cost_matrix(self):
        self.assertRaises(
            ValueError,
            uncertainty_scores,
            self.probas,
            cost_matrix=np.ones((2, 3)),
        )
        self.assertRaises(
            ValueError, uncertainty_scores, self.probas, cost_matrix="string"
        )
        self.assertRaises(
            ValueError,
            uncertainty_scores,
            self.probas,
            cost_matrix=np.ones((2, 2)),
        )

    def test_uncertainty_scores(self):
        # least_confident
        val_scores = np.array([0.5, 0.3])
        scores = uncertainty_scores(self.probas, method="least_confident")
        np.testing.assert_allclose(val_scores, scores)
        # entropy
        val_scores = np.array([1.029653014, 0.8018185525])
        scores = uncertainty_scores(self.probas, method="entropy")
        np.testing.assert_allclose(val_scores, scores)
        # margin_sampling
        val_scores = np.array([0.8, 0.5])
        scores = uncertainty_scores(self.probas, method="margin_sampling")
        np.testing.assert_allclose(val_scores, scores)
