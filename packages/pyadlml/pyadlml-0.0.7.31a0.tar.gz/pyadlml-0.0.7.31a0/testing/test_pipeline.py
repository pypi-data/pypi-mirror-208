from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KernelDensity
from sklearn.svm import SVC
from pyadlml.pipeline import Pipeline
from pyadlml.preprocessing import StateVectorEncoder, DropTimeIndex, LabelMatcher
from pyadlml.constants import *
from pyadlml.dataset import load_act_assist
import unittest
import sys
import pathlib
working_directory = pathlib.Path().absolute()
script_directory = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(working_directory))


class TestPipeline(unittest.TestCase):
    def setUp(self):
        dataset_dir = str(script_directory) + '/datasets/partial_dataset'
        self.data = load_act_assist(dataset_dir)
        self.df_acts = self.data['activities']
        self.df_devs = self.data['devices']

        self.rf_pipe = [
            ('raw', StateVectorEncoder(encode='raw')),
            ('lbl', LabelMatcher(idle=True)),
            ('drop_tidx', DropTimeIndex()),
            ('classifier', RandomForestClassifier(random_state=42))
        ]
        self.kde_pipe = [
            ('raw', StateVectorEncoder(encode='raw')),
            ('drop_tidx', DropTimeIndex()),
            ('classifier', KernelDensity(kernel='gaussian', bandwidth=0.5))
        ]
        self.svm_pipe = [
            ('raw', StateVectorEncoder(encode='raw')),
            ('lbl', LabelMatcher(idle=True)),
            ('drop_tidx', DropTimeIndex()),
            ('classifier', SVC())
        ]

    # def test_decision_function(self):
    #    #  Apply transforms, and decision_function of the final estimator
    #    pipe = Pipeline(self.svm_pipe)
    #    pipe = pipe.fit(df_devs,
    #                df_acts)
    #    tmp = pipe.decision_function(df_devs)

    def test_fit(self):
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()
        pipe = Pipeline(self.rf_pipe)
        tmp = pipe.fit(df_devs,
                       df_acts)

    def test_fit_predict(self):
        # Applies fit_predict of last step in pipeline after transforms.

        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()
        pipe = Pipeline(self.rf_pipe)
        tmp = pipe.fit_predict(
            df_devs,
            df_acts)
        print(tmp)

    def test_fit_transform(self):
        # Fit the model and transform with the final estimator
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe)
        tmp = pipe.fit_transform(
            df_devs,
            df_acts)

    def test_get_params(self):
        # Get parameters for this estimator.
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe)
        tmp = pipe.get_params()
        # print(tmp)

    def test_predict(self):
        # Apply transforms to the data, and predict with the final estimator
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe).fit(
            df_devs, df_acts)
        tmp = pipe.predict(df_devs)
        print(tmp)

    def test_predict_log_proba(self):
        # Apply transforms, and predict_log_proba of the final estimator
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe).fit(
            df_devs, df_acts)
        tmp = pipe.predict_log_proba(df_devs)
        print(tmp)

    def test_predict_proba(self):
        # Apply transforms, and predict_proba of the final estimator
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe).fit(
            df_devs, df_acts)
        tmp = pipe.predict_proba(df_devs)
        print(tmp)

    def test_score(self):
        # Apply transforms, and score with the final estimator
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.rf_pipe).fit(
            df_devs, df_acts)
        tmp = pipe.score(
            df_devs,
            df_acts)
        print(tmp)

    def test_score_samples(self):
        # Apply transforms, and score_samples of the final estimator.
        df_devs, df_acts = self.df_acts.copy(), self.df_devs.copy()

        pipe = Pipeline(self.kde_pipe).fit(df_devs)
        tmp = pipe.score_samples(df_devs)
        print(tmp)


if __name__ == '__main__':
    unittest.main()
