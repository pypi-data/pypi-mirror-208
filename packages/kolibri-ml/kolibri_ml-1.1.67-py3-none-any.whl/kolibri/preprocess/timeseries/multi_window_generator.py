from math import ceil
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from kolibri.core.component import Component
import tensorflow as tf
from kolibri.utils.timeseries_functions import roll_time_series
#from tensorflow.keras.preprocessing.sequence import pad_sequences


class MultiWindowGenerator(Component):
    """Base class for sliding and expanding window splitter."""

    defaults = {
        "fixed": {
            "target": None,
            "dropnan": True,
            "shuffle": False,
            "seed": None,
            "batch-size": 32,
            "buffer-size": 150,
            "timestamp-test": 1,
            "timestamp-val": 1,
            "group": [],
            "timestamp": [],
            "univariate": False,
            "horizon": 1,
            "n_jobs": 4,
            "sets": ["val", "test"],  # or "predict"
            "main-period": -1
        },
        "tunable": {
            "min-window-history": {
                "value": 1
            },
            "max-window-history": {
                "value": 4
            }
        }

    }

    def __init__(self, data, configs={}):
        super(MultiWindowGenerator, self).__init__(configs)
        self._split_sets=self.get_parameter("sets")
        assert set(self._split_sets) < set(["val", "test", "predict"])

        self.data = data
        nb_timestamps = len(sorted(self.data[self.get_parameter("timestamp")].unique()))

        if len(self._split_sets)+1 > nb_timestamps:
            raise Exception(
                "Not enough periods in the data expecting at least" + str(
                    len(self._split_sets)+1) + " periods, but getting " + str(nb_timestamps) + " periods")

        self.seed = self.get_parameter("seed")

        self._extra_columns = list(
            filter(None, [self.get_parameter("group"), self.get_parameter("timestamp"), "id", "id_sort"]))

        self.column_indices = None

        # Work out the label column indices.
        self.targets = self.get_parameter("target")

        # Work out the window parameters.
        self.window_length = self.get_parameter("max-window-history")
        self.horizon = self.get_parameter("horizon")
        self.shift = self.get_parameter("shift", 1)
        self.shuffle = self.get_parameter("shuffle")
        self.label_columns_indices = None
        if self.targets is not None:
            self.label_columns_indices = {name: i for i, name in
                                          enumerate(self.targets)}

        self.total_window_size = self.window_length + self.horizon

        self.input_slice = slice(0, self.window_length)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.horizon
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]
        self._roll_data()
        if set(self._split_sets) <= set(["val", "test"]):
            self.split_train_test_val()
        elif self._split_sets ==["predict"]:
            self.get_main_set()
        if self.column_indices is None and len(self._train_df)>0:
            columns = [col for col in self._train_df[0].columns if col not in self._extra_columns]
            if self._train_df is not None:
                self.column_indices = {name: i for i, name in
                                       enumerate(columns)}

    def __repr__(self):
        return '\n'.join([
            f'Total window size: {self.total_window_size}',
            f'Input indices: {self.input_indices}',
            f'Label indices: {self.label_indices}',
            f'Label column name(s): {self.targets}'])

    def split_window(self, features):
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]

        if self.targets is not None:
            labels = np.stack(
                [labels[:, :, self.column_indices[name]] for name in self.targets],
                axis=-1)

        return inputs, labels

    def plot(self, model=None, plot_col='Gross_Total', max_subplots=3):
        inputs, labels = self.example
        plt.figure(figsize=(12, 8))
        plot_col_index = self.column_indices[plot_col]
        max_n = min(max_subplots, len(inputs))
        for n in range(max_n):
            plt.subplot(max_n, 1, n + 1)
            plt.ylabel(f'{plot_col} [normed]')
            plt.plot(self.input_indices, inputs[n, :, plot_col_index],
                     label='Inputs', marker='.', zorder=-10)

            if self.targets:
                label_col_index = self.label_columns_indices.get(plot_col, None)
            else:
                label_col_index = plot_col_index

            if label_col_index is None:
                continue

            plt.scatter(self.label_indices, labels[n, :, label_col_index],
                        edgecolors='k', label='Labels', c='#2ca02c', s=64)
            if model is not None:
                predictions = model(inputs)
                plt.scatter(self.label_indices, predictions[n, :, label_col_index],
                            marker='X', edgecolors='k', label='Predictions',
                            c='#ff7f0e', s=64)

            if n == 0:
                plt.legend()

        plt.xlabel('Time')
        return plt

    def _roll_data(self):
        if self.get_parameter("dropnan"):
            self.data = self.data.fillna(0)

        self.df_rolled = roll_time_series(self.data, column_id=self.get_parameter("group"),
                                          column_sort=self.get_parameter("timestamp"),
                                          n_jobs=self.get_parameter("n_jobs"),
                                          max_timeshift=self.get_parameter("max-window-history") + self.horizon - 1,
                                          min_timeshift=self.get_parameter(
                                              "min-window-history") + self.horizon - 1)
#        df_rolled=[df.drop(
#            columns=[self.get_parameter("group"), self.get_parameter("timestamp")]) for df in df_rolled]


        for df in self.df_rolled:
            df.drop(columns=[self.get_parameter("group"), self.get_parameter("timestamp")], inplace=True)
            df[['id_group', 'id_sort']]=pd.DataFrame(df['id'].tolist(),index=df.index)

        return
    def split_train_test_val(self):
        timestamps = sorted(self.data[self.get_parameter("timestamp")].unique())
        valid_timestamp=None
        test_timestamp=None


        if "val" in self._split_sets:
            valid_timestamp = timestamps[-(self._split_sets.index("val")+2)]
            self._valid_df = [df[df["id_sort"] == valid_timestamp] for df in self.df_rolled if len(df[df["id_sort"] == valid_timestamp])>0]

        if "test" in self._split_sets:
            test_timestamp = timestamps[-(self._split_sets.index("test"))]
            self._test_df =[df[df["id_sort"] == test_timestamp] for df in self.df_rolled if len(df[df["id_sort"] == test_timestamp])>0]

        if valid_timestamp or test_timestamp:
            train_timestamp=min(value for value in [valid_timestamp, test_timestamp] if value is not None)
            self._train_df = [df[df["id_sort"] < train_timestamp] for df in self.df_rolled if len(df[df["id_sort"] < train_timestamp])>0]
        else:
            self._train_df = self.df_rolled

    def get_main_set(self):
        main_period=self.get_parameter("main-period")
        timestamps = sorted(self.data[self.get_parameter("timestamp")].unique())

        main_timestamp=-1
        if main_period is not None:
            if isinstance(main_period, int):
                if abs(main_period)>=len(timestamps):
                    raise Exception("The Index of the target period, " + str(main_period) + " is greater the number of periods of the dataset, (" + str(len(timestamps)) + "periods)")
                main_timestamp=timestamps[main_period]
            elif isinstance(main_period, datetime.datetime):
                main_timestamp=main_period
            else:
                raise Exception("Wrong 'main-period' format. Should be either an integer or a datatime.")
        self._train_df = [df[df["id_sort"] == main_timestamp] for df in self.df_rolled]

     #   self._train_df = self.df_rolled[main_timestamp]

    def _get_array_values(self, ds, drop_ids=None):

#        values = ds.groupby(["id", "id_sort"])
        colums_to_drop = ["id", "id_sort", "id_group"]
        dtypes = 'float32'
        if drop_ids is not None:
            colums_to_drop = drop_ids
            dtypes = 'object'
        if self.get_parameter('max-window-history') == self.get_parameter('min-window-history'):
            values = [d[1].drop(columns=colums_to_drop).values for df in ds for d in df.groupby(["id_group"])]

        else:
            values = [tf.keras.preprocessing.sequence.pad_sequences(
                d[1].drop(columns=colums_to_drop).values.T, dtype=dtypes, padding='pre',
                maxlen=self.get_parameter('max-window-history')+self.get_parameter('horizon'), value=0.0).T for df in ds for d in df.groupby(["id_group"])]

            # values = [tf.keras.preprocessing.sequence.pad_sequences(
            #     df.drop(columns=colums_to_drop).values.T, dtype=dtypes, padding='pre',
            #     maxlen=self.get_parameter('max-window-history')+self.get_parameter('horizon'), value=0.0).T  for df in ds]


        return np.rollaxis(np.dstack(values), -1)

    @property
    def train(self):

        if not hasattr(self, "train_values"):
            self.train_values = self.split_window(self._get_array_values(self._train_df))

        return self.train_values

    @property
    def main(self):
        return self.train

    @property
    def train_ds(self):

        BUFFER_SIZE = self.get_parameter("buffer-size")
        BATCH_SIZE = self.get_parameter("batch-size")

        train_data_multi = tf.data.Dataset.from_tensor_slices(self.train)
        train_data_multi = train_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return train_data_multi

    @property
    def val(self):

        if not hasattr(self, "val_values"):
            self.val_values = self.split_window(self._get_array_values(self._valid_df))

        return self.val_values

    @property
    def val_ds(self):
        BUFFER_SIZE = self.get_parameter("buffer-size")
        BATCH_SIZE = self.get_parameter("batch-size")

        val_data_multi = tf.data.Dataset.from_tensor_slices(self.val)
        val_data_multi = val_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return val_data_multi

    @property
    def test(self):
        if not hasattr(self, "test_values"):
            self.test_values = self.split_window(self._get_array_values(self._test_df))
        return self.test_values

    @property
    def test_ds(self):
        BUFFER_SIZE = self.get_parameter("buffer-size")
        BATCH_SIZE = self.get_parameter("batch-size")

        test_data_multi = tf.data.Dataset.from_tensor_slices(self.test)
        test_data_multi = test_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return test_data_multi

    @property
    def main_ds(self):
        return self.train_ds


    @property
    def num_features(self):
        return len(self._train_df.columns) - len(self._extra_columns)

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, '_example', None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train_ds))
            # And cache it for next time
            self._example = result

        return result

    @property
    def train_df(self):
        return pd.concat([df.drop(columns=["id", "id_sort", "id_group"]) for df in self._train_df])

    @property
    def main_df(self):
        if hasattr(self, "main_df_"):
            return self.main_df_
        else:
            main_values = self._get_array_values(self._train_df, drop_ids=["id"])
            self.main_df_ = pd.DataFrame(main_values[:, self.labels_slice, :].reshape(-1, main_values.shape[2]),
                                         columns=list(self.train_df.columns) + ["id_group", "id_sort"])
        return self.main_df_

    @property
    def test_df(self):
        if hasattr(self, "test_df_"):
            return self.test_df_
        else:
            test_values = self._get_array_values(self._test_df, drop_ids=["id"])
            self.test_df_ = pd.DataFrame(test_values[:, self.labels_slice, :].reshape(-1, test_values.shape[2]),
                                         columns=list(self.train_df.columns) + ["id_group", "id_sort"])
        return self.test_df_

    @property
    def val_df(self):
        if hasattr(self, "val_df_"):
            return self.val_df_
        else:
            val_values = self._get_array_values(self._valid_df, drop_ids=["id"])
            self.val_df_ = pd.DataFrame(val_values[:, self.labels_slice, :].reshape(-1, val_values.shape[2]),
                                        columns=list(self.train_df.columns) + ["id_group", "id_sort"])
        return self.val_df_

    def process_timestep(self, df, history_df=None, ovrride_timestamps=False):

        if self.data is None:
            self.data = history_df

        if self.data is None or len(self.data.index) < 1:
            raise Exception("History data set is empty of Null")

        if self.get_parameter("timestamp") not in df.columns or self.get_parameter(
                "timestamp") not in self.data.columns:
            raise Exception(
                "Timestamp column: " + self.get_parameter("timestamp") + " not found in the provided dataframe")

        history_window_length = self.get_parameter("max-window-history")
        timestamps = sorted(self.data[self.get_parameter("timestamp")].unique())[:-history_window_length]
        self.data = self.data[self.data[self.get_parameter("timestamp")].isin(timestamps)]
        new_time_steps = sorted(df[self.get_parameter("timestamp")].unique())[:-history_window_length]

        if new_time_steps[0] <= timestamps[-1] and not ovrride_timestamps:
            raise Exception("The provided timestep already exist in history")

        if len(self.data.columns.intersection(df.columns)) != self.data.shape[1]:
            raise Exception("History and the provided dataset does nbot have the same columns")

        self.data = pd.concat([self.data, df[self.data.columns.intersection(df.columns)]])

        self.df_predict = roll_time_series(self.data, column_id=self.get_parameter("group"),
                                           column_sort=self.get_parameter("timestamp"),
                                           max_timeshift=self.get_parameter("max-window-history") + self.horizon - 1,
                                           min_timeshift=self.get_parameter(
                                               "min-window-history") + self.horizon - 1).drop(
            columns=[self.get_parameter("group"), self.get_parameter("timestamp")])

        self.df_predict[['id_group', 'id_sort']] = pd.DataFrame(self.df_rolled['id'].tolist(),
                                                                index=self.df_rolled.index)
        predict_values = self.split_window(self._get_array_values(self.df_predict))

        return predict_values


if __name__=="__main__":
    data=pd.read_csv("/Users/mohamedmentis/Downloads/test_2periods.csv")
    configs={"timestamp": "Original_Start_Date", "target": [35], "sets": ["predict"],  "group":'Employee_Id'}
    mwg=MultiWindowGenerator(data, configs=configs)

    print(mwg.train())