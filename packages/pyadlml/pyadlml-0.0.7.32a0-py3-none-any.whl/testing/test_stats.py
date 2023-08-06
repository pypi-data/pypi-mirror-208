from pyadlml.constants import *
from pyadlml.dataset import load_act_assist
import unittest
import sys
import pathlib
working_directory = pathlib.Path().absolute()
script_directory = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(working_directory))


class TestDirtyDataset(unittest.TestCase):
    def setUp(self):
        dataset_dir = str(script_directory) + '/datasets/diry_dataset'
        self.data = load_act_assist(dataset_dir)
        self.df_acts = self.data['activities']
        self.df_devs = self.data['devices']

    def test_stats_activities(self):
        from pyadlml.dataset.stats.activities import activities_dist, activities_count, \
            activities_transitions, activities_duration_dist

        df_acts = self.df_acts.copy()
        lst = self.data['list_activities']

        act_count = activities_count(df_acts, lst)
        assert len(act_count) == len(lst)
        act_count = activities_count(df_acts)
        assert len(act_count) == 2

        act_trans = activities_transitions(df_acts, lst)
        assert len(act_trans) == len(lst)
        assert act_trans.values.sum() == len(df_acts) - 1
        act_trans = activities_transitions(df_acts)
        assert len(act_trans) == 2

        act_durs = activities_duration_dist(df_acts, lst)
        assert len(act_durs) == len(lst)
        act_durs = activities_duration_dist(df_acts)
        assert len(act_durs) == 2

        act_dist = activities_dist(df_acts, lst, n=100)
        assert len(act_dist.columns) == len(lst)
        assert len(act_dist) == 100
        act_dist = activities_dist(df_acts, n=100)
        assert len(act_dist.columns) == 2
        assert len(act_dist) == 100

    def test_stats_devices(self):
        from pyadlml.dataset.stats.devices import event_count, events_one_day,\
            inter_event_intervals, state_fractions, state_cross_correlation

        df_devs = self.df_devs.copy()
        lst = self.data['device_lst']

        num_rec_devs = 5  # only those devices that appear in devices.csv
        num_rec_binary_devs = 3

        # tcorr = device_tcorr(df)
        tcorr = device_tcorr(df_devs, lst)
        assert tcorr.shape[0] == len(lst) and tcorr.shape[1] == len(lst)

        trigg_c = devices_trigger_count(df_devs)
        assert len(trigg_c) == num_rec_devs
        trigg_c = devices_trigger_count(df_devs, lst)
        assert len(trigg_c) == len(lst)

        trigg_od = device_triggers_one_day(df_devs)
        assert len(trigg_od.columns) == num_rec_devs
        trigg_od = device_triggers_one_day(df_devs,  lst)
        assert len(trigg_od.columns) == len(lst)

        trigg_td = trigger_time_diff(df_devs)
        assert len(trigg_td) == len(df_devs) - 1

        onoff = devices_on_off_stats(df_devs)
        assert len(onoff) == num_rec_binary_devs
        onoff = devices_on_off_stats(df_devs, lst)
        assert len(onoff) == len(lst)

        dc = duration_correlation(df_devs)
        assert len(dc) == num_rec_binary_devs
        dc = duration_correlation(df_devs, lst)
        assert len(dc) == len(lst)

    def test_plot_activities(self):
        from pyadlml.dataset.plot.activities import activities_duration_dist, boxplot_duration, \
            heatmap_transitions, hist_cum_duration, ridge_line, hist_counts

        df = self.data.df_activities_admin
        lst = self.data.lst_activities

        hist_counts(df)
        hist_counts(df, lst_act=lst)

        boxplot_duration(df)
        boxplot_duration(df, lst_act=lst)

        hist_cum_duration(df)
        hist_cum_duration(df, act_lst=lst)

        heatmap_transitions(df)
        heatmap_transitions(df, lst_act=lst)

        ridge_line(df)
        ridge_line(df, lst_act=lst, n=10)

    def test_plot_devices(self):
        from pyadlml.dataset.plot.devices import hist_counts, heatmap_trigger_one_day, heatmap_trigger_time,\
            hist_on_off, boxplot_on_duration, heatmap_cross_correlation, hist_trigger_time_diff

        df = self.data.df_devices
        lst = self.data.lst_devices

        hist_counts(df)
        hist_counts(df_dev=df, lst_dev=lst)

        heatmap_trigger_one_day(df)
        heatmap_trigger_one_day(df, lst_dev=lst)

        heatmap_trigger_time(df)
        heatmap_trigger_time(df, lst_dev=lst)

        hist_trigger_time_diff(df)

        hist_on_off(df)
        hist_on_off(df, lst_dev=lst)

        boxplot_on_duration(df)
        boxplot_on_duration(df, lst_dev=lst)

        heatmap_cross_correlation(df)
        heatmap_cross_correlation(df, lst_dev=lst)


if __name__ == '__main__':
    unittest.main()
