import unittest

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

from skactiveml.classifier import PWC
from skactiveml.pool.multi import IEThresh, IEAnnotModel


class TestIEAnnotModel(unittest.TestCase):

    def setUp(self):
        self.y = np.array([[1, np.nan, 1, 0],
                           [0, np.nan, 1, 1],
                           [0, np.nan, 0, 0],
                           [0, np.nan, 1, 0]])
        self.sample_weight = np.array([[1, np.nan, 1, 1],
                                       [1, np.nan, 1, 1],
                                       [1, np.nan, 1, 1],
                                       [1, np.nan, 3, 1]])

    def test_init_param_classes(self):
        ie_model = IEAnnotModel(classes='test')
        self.assertRaises(ValueError, ie_model.fit, y=self.y)
        ie_model = IEAnnotModel(classes=[0])
        self.assertRaises(ValueError, ie_model.fit, y=self.y)

    def test_init_param_missing_label(self):
        ie_model = IEAnnotModel(missing_label=['test'])
        self.assertRaises(TypeError, ie_model.fit, y=self.y)
        ie_model = IEAnnotModel(missing_label='o')
        self.assertRaises(ValueError, ie_model.fit, y=self.y)

    def test_init_param_alpha(self):
        ie_model = IEAnnotModel(alpha=0.0)
        self.assertRaises(ValueError, ie_model.fit, y=self.y)
        ie_model = IEAnnotModel(alpha=1.0)
        self.assertRaises(ValueError, ie_model.fit, y=self.y)
        ie_model = IEAnnotModel(alpha='test')
        self.assertRaises(TypeError, ie_model.fit, y=self.y)

    def test_init_param_mode(self):
        ie_model = IEAnnotModel(mode='test')
        self.assertRaises(ValueError, ie_model.fit, y=self.y)

    def test_init_param_random_state(self):
        ie_model = IEAnnotModel(random_state='test')
        self.assertRaises(ValueError, ie_model.fit, y=self.y)

    def test_fit_param_y(self):
        ie_model = IEAnnotModel()
        self.assertRaises(ValueError, ie_model.fit, y=np.ones(4))
        self.assertRaises(TypeError, ie_model.fit, y='test')

    def test_fit_param_sample_weight(self):
        ie_model = IEAnnotModel()
        self.assertRaises(ValueError, ie_model.fit, y=self.y,
                          sample_weight=np.ones(len(self.y)))
        self.assertRaises(TypeError, ie_model.fit, y=self.y,
                          sample_weight='test')

    def test_predict_annot_perf_param_X(self):
        ie_model = IEAnnotModel().fit(self.y)
        self.assertRaises(ValueError, ie_model.predict_annot_proba, X=None)
        self.assertRaises(ValueError, ie_model.predict_annot_proba,
                          X=np.ones(2))

    def test_fit(self):
        ie_model = IEAnnotModel().fit(self.y, sample_weight=self.sample_weight)
        np.testing.assert_array_equal(ie_model.A_perf_.shape,
                                      (self.y.shape[1], 3))
        self.assertEqual(ie_model.A_perf_[2, 1], 5/6)
        a_idx, mode_idx = np.unravel_index(np.argmax(ie_model.A_perf_),
                                           ie_model.A_perf_.shape)
        self.assertTrue(a_idx, 1)
        self.assertTrue(mode_idx, 2)

    def test_predict_proba(self):
        for i, m in enumerate(['lower', 'mean', 'upper']):
            ie_model = IEAnnotModel(mode=m)
            ie_model.fit(self.y, sample_weight=self.sample_weight)
            P_annot = ie_model.predict_annot_proba(X=np.ones((10, 2)))
            np.testing.assert_array_equal(P_annot[0], ie_model.A_perf_[:, i])
            self.assertEqual(len(P_annot), 10)


class TestIEThresh(unittest.TestCase):

    def setUp(self):
        self.X, y_true = make_blobs(n_samples=10, random_state=0)
        self.X = StandardScaler().fit_transform(self.X)
        self.y = np.array([y_true, y_true, y_true, y_true], dtype=float).T
        self.y[:, 1] = 1
        self.y[:, 0] = 0
        self.y[1:5, 2] = np.nan
        self.clf = PWC()
        self.A_cand = np.ones_like(self.y)
        self.sample_weight = np.ones_like(self.y)

    def test_init_param_alpha(self):
        ie_thresh = IEThresh(alpha=0.0, random_state=0)
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)
        ie_thresh = IEThresh(alpha=1.0, random_state=0)
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)
        ie_thresh = IEThresh(alpha='test', random_state=0)
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)

    def test_init_param_epsilon(self):
        ie_thresh = IEThresh(epsilon=-0.1, random_state=0)
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)
        ie_thresh = IEThresh(alpha=1.1, random_state=0)
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)
        ie_thresh = IEThresh(epsilon='test', random_state=0)
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)

    def test_init_param_n_annotators(self):
        ie_thresh = IEThresh(n_annotators='test')
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, X=self.X, y=self.y)

    def test_init_param_random_state(self):
        ie_thresh = IEThresh(random_state='test')
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y)

    def test_query_param_X_cand(self):
        ie_thresh = IEThresh()
        self.assertRaises(ValueError, ie_thresh.query,
                          clf=self.clf, X_cand=np.ones((10, 10)), X=self.X,
                          y=self.y, A_cand=np.ones((10, self.y.shape[1])))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=np.ones(10), clf=self.clf, X=self.X, y=self.y,
                          A_cand=np.ones((10, self.y.shape[1])))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand='test', clf=self.clf, X=self.X, y=self.y,
                          A_cand=np.ones((10, self.y.shape[1])))

    def test_init_param_clf(self):
        ie_thresh = IEThresh()
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X, clf=None,
                          A_cand=self.A_cand, X=self.X, y=self.y)

    def test_query_param_A_cand(self):
        ie_thresh = IEThresh()
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X, y=self.y,
                          A_cand=np.ones((len(self.X)+1, self.y.shape[1])))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X, y=self.y,
                          A_cand=np.ones((len(self.X), self.y.shape[1]+1)))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X, y=self.y,
                          A_cand='test')

    def test_query_param_X(self):
        ie_thresh = IEThresh()
        self.assertRaises(ValueError, ie_thresh.query,
                          X=np.ones((10, 10)), X_cand=self.X, clf=self.clf,
                          y=self.y, A_cand=self.A_cand)
        self.assertRaises(ValueError, ie_thresh.query,
                          X=np.ones(10), X_cand=self.X, clf=self.clf,  y=self.y,
                          A_cand=self.A_cand)
        self.assertRaises(TypeError, ie_thresh.query,
                          X='test', X_cand=self.X, clf=self.clf, y=self.y,
                          A_cand=self.A_cand)

    def test_query_param_y(self):
        ie_thresh = IEThresh()
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X,
                          y=np.ones(len(self.X)), A_cand=self.A_cand)
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X,
                          A_cand=self.A_cand,
                          y=np.ones((len(self.X) + 1, self.A_cand.shape[1])))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, clf=self.clf, X=self.X,
                          A_cand=self.A_cand,
                          y=np.ones((len(self.X), self.A_cand.shape[1]+1)))
        self.assertRaises(TypeError, ie_thresh.query,
                          X_cand=self.X, X=self.X, A_cand=self.A_cand,
                          y='test')

    def test_query_param_sample_weight(self):
        ie_thresh = IEThresh()
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, X=self.X,
                          y=self.y, A_cand=self.A_cand,
                          sample_weight=np.ones(len(self.X)))
        sample_weight = np.ones((len(self.X) + 1, self.A_cand.shape[1]))
        self.assertRaises(ValueError, ie_thresh.query, X_cand=self.X, X=self.X,
                          clf=self.clf, A_cand=self.A_cand, y=self.y,
                          sample_weight=sample_weight)
        sample_weight = np.ones((len(self.X) + 1, self.A_cand.shape[1]))
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, X=self.X, A_cand=self.A_cand,
                          clf=self.clf, y=self.y, sample_weight=sample_weight)
        self.assertRaises(ValueError, ie_thresh.query,
                          X_cand=self.X, X=self.X, A_cand=self.A_cand,
                          clf=self.clf, y=self.y, sample_weight='test')

    def test_query_param_batch_size(self):
        ie_thresh = IEThresh()
        for wrong_batch_size, error in [(0, ValueError),
                                        ('test', ValueError),
                                        (None, TypeError)]:
            self.assertRaises(error, ie_thresh.query, X_cand=self.X,
                              clf=self.clf, A_cand=self.A_cand, X=self.X,
                              y=self.y, batch_size=wrong_batch_size)

    def test_query_param_return_utilities(self):
        ie_thresh = IEThresh()
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y,
                          return_utilities=0)
        ie_thresh = IEThresh()
        self.assertRaises(TypeError, ie_thresh.query, X_cand=self.X,
                          clf=self.clf, A_cand=self.A_cand, X=self.X, y=self.y,
                          return_utilities='test')

    def test_query(self):
        ie_thresh = IEThresh(epsilon=1.0)
        batch_sizes = [self.A_cand.shape[1], 60, 'adaptive', 7]
        actual_batch_sizes = [self.A_cand.shape[1], 40, 1, 7]
        n_samples = [1, 10, 1, 2]
        for b_in, b_act, n in zip(batch_sizes, actual_batch_sizes, n_samples):
            query_indices, utilities = ie_thresh.query(X_cand=self.X, clf=PWC(),
                                                       X=self.X, y=self.y,
                                                       A_cand=self.A_cand,
                                                       return_utilities=True,
                                                       batch_size=b_in)
            np.testing.assert_array_equal(query_indices.shape, [b_act, 2])
            np.testing.assert_array_equal(
                utilities.shape,
                [b_act, len(self.X), self.y.shape[1]]
            )
            for b in range(len(utilities)):
                self.assertEqual(b, np.sum(np.isnan(utilities[b])))
            self.assertEqual(len(np.unique(query_indices[:, 0])), n)
            query_indices = ie_thresh.query(X_cand=self.X, clf=PWC(), X=self.X,
                                            y=self.y, A_cand=self.A_cand,
                                            batch_size=b_in)
            np.testing.assert_array_equal(query_indices.shape, [b_act, 2])

        A_cand = np.zeros_like(self.y)
        query_indices, utilities = ie_thresh.query(X_cand=self.X, X=self.X,
                                                   clf=PWC(), y=self.y,
                                                   A_cand=A_cand,
                                                   return_utilities=True)
        self.assertEqual(len(query_indices), 0)
        self.assertEqual(len(utilities), 0)
        query_indices = ie_thresh.query(X_cand=self.X, X=self.X, clf=PWC(),
                                        y=self.y, A_cand=A_cand)
        self.assertEqual(len(query_indices), 0)

    def test_query_with_variant_available_annotators(self):

        ie_thresh = IEThresh(epsilon=1.0)
        A_cand = np.array([[True, True, True, True],
                           [True, False, False, False],
                           [True, True, True, False]])

        n_a_annotators = np.sum(A_cand, axis=1)

        X_cand = np.array([[0.0, 1.0],
                           [1.0, 1.0],
                           [1.0, 0.0]])

        query_indices, utilities = ie_thresh.query(X_cand=X_cand, clf=PWC(),
                                                   X=self.X, y=self.y,
                                                   A_cand=A_cand,
                                                   return_utilities=True,
                                                   batch_size=7)

        for index in range(len(query_indices)-1):
            self.assertGreaterEqual(n_a_annotators[query_indices[index, 0]],
                                    n_a_annotators[query_indices[index+1, 0]])

