from pyadlml.constants import *
from pyadlml.dataset import load_act_assist
import unittest
import sys
import pathlib

from pyadlml.feature_extraction import DayOfWeek, extract_time_difference
working_directory = pathlib.Path().absolute()
script_directory = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(working_directory))


class TestDirtyDataset(unittest.TestCase):
    def setUp(self):
        dataset_dir = script_directory.joinpath('/datasets/dirty_dataset')
        self.data = load_act_assist(dataset_dir)
        self.df_acts = self.data['activities']
        self.df_devs = self.data['devices']

    def test_extract_time_bins(self):
        df_devs = self.df_devs.copy()
        df_res2h = extract_time_difference(df_devs)
        df_res6h = extract_time_difference(df_devs, resolution='6h')
        df_res10m = extract_time_difference(df_devs, resolution='10m')
        df_res40m = extract_time_difference(df_devs, resolution='40m')
        df_res10s = extract_time_difference(df_devs, resolution='10s')

        assert len(df_res2h.columns) == 12
        assert len(df_res6h.columns) == 4
        assert len(df_res10m.columns) == 144
        assert len(df_res40m.columns) == 36
        assert len(df_res10s.columns) == 8640

    def test_extract_day_of_week(self):
        df_devs = self.df_devs.copy()
        df_dow = DayOfWeek(one_hot_encoding=False)


if __name__ == '__main__':
    unittest.main()
