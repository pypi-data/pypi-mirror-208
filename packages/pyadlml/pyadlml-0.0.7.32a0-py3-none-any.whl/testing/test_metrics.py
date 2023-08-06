import numpy as np
import pandas as pd
from pyadlml.constants import *
from pyadlml.dataset import load_act_assist
import unittest
import sys
import pathlib

from pyadlml.dataset._core.activities import add_other_activity
working_directory = pathlib.Path().absolute()
script_directory = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(working_directory))


class TestMetrics(unittest.TestCase):
    def setUp(self):
        dataset_dir = str(script_directory) + '/datasets/debug_dataset'
        self.data = load_act_assist(dataset_dir)
        self.df_acts = self.data['activities']['chris']
        self.df_devs = self.data['devices']

    def _gen_identical(self, df_acts, other=False):
        df = add_other_activity(df_acts) if other else df_acts
        y_true = df[ACTIVITY].to_numpy()
        y_true_times = df[START_TIME].to_numpy()
        return y_true, y_true_times

    def _gen(df_acts, self):
        y_pred = df_acts[ACTIVITY]
        y_times = np.array([pd.Timestamp(ts) for ts in ['']])

    def test_online_acc(self):
        df_devs, df_acts = self.df_devs.copy(), self.df_acts.copy()
        activities = np.append(df_acts[ACTIVITY].unique(), 'other')
        from pyadlml.metrics import online_accuracy

        # Check if identity is one
        y_true, y_true_times = self._gen_identical(df_acts, other=True)
        # acc_micro = online_accuracy(df_acts, y_true, y_true_times,
        #                            len(activities), average='micro')
        # assert np.isclose(acc_micro, 1.0, atol=0.001)
        acc_macro = online_accuracy(df_acts, y_true, y_true_times,
                                    len(activities), average='macro')
        assert np.isclose(acc_macro, 1.0, atol=0.001)

        # Check if without other is one
        y_pred, y_pred_times = self._gen_identical(df_acts, other=False)
        acc_micro = online_accuracy(df_acts, y_pred, y_pred_times,
                                    len(activities), average='micro')
        acc_true = 0.874
        assert np.isclose(acc_micro, acc_true, atol=0.001), \
            f'Should have {acc_true} but got {acc_micro}'

        acc_macro = online_accuracy(df_acts, y_pred, y_pred_times,
                                    len(activities), average='macro')
        assert np.isclose(acc_macro, acc_true, atol=0.001), \
            f'Should have {acc_true} but got {acc_macro}'

    def test_online_ppv(self):
        df_devs, df_acts = self.df_devs.copy(), self.df_acts.copy()

    def test_online_tpr(self):
        df_devs, df_acts = self.df_devs.copy(), self.df_acts.copy()

    def test_online_conf_mat(self):
        df_devs, df_acts = self.df_devs.copy(), self.df_acts.copy()


if __name__ == '__main__':
    unittest.main()
