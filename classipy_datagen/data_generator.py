import numpy as np
import pandas as pd
from scipy.stats import shapiro
from os.path import normpath, join, abspath, dirname


class DataGenerator:
    def __init__(self, n_samples=1000, n_datasets=None, output_name=None, to_json=True) -> None:
        self.n_samples = n_samples
        self.output_name = output_name
        self.n_datasets = n_datasets
        self.to_json = to_json
        self.loc_data = normpath(
            join(dirname(dirname(__file__)), 'raw_data'))

    def get_dataframe(self, df, dataset_name, table_name):
        print(f'Processing DataFrame: {dataset_name} {table_name}')
        df_rows = [
            self.get_row(df[col_name], dataset_name, table_name) for col_name in df
        ]
        return pd.concat(df_rows, axis=0).reset_index(drop=True)

    def get_row(self, column, dataset_name, table_name):
        try:
            col = column.sample(self.n_samples)
        except ValueError:
            col = column

        features = {
            "dataset_name": [dataset_name],
            "table_name": [table_name],
            "column_name": [column.name],
            "label": [np.nan],
        }

        feature_functions = {
            "column_values": lambda x: ", ".join(map(str, x.tolist())),
            "column_values_unique": lambda x: x.unique(),
            "n_unique_values": lambda x: x.nunique(),
            "unique_value_counts": lambda x: {val: freq for val, freq in x.value_counts().items()},
            'n_values': lambda x: x.shape[0],
            "mean": lambda x: x.mean(),
            "std": lambda x: x.std(),
            "median": lambda x: x.median(),
            "skew": lambda x: x.skew(),
            "kurt": lambda x: x.kurt(),
            "shapiro_wilk_test": lambda x: shapiro(x)[1],
        }

        for col_name, fn in feature_functions.items():
            try:
                val = fn(col)
            except (ValueError, TypeError):
                val = np.nan
            except Exception as e:  # DEBUGGING TYPES OF ERRORS
                val = np.nan
                print(features['column_name'], col_name, 'Exception:', type(e))

            features[col_name] = [val]

        return pd.DataFrame.from_dict(features)

    def download_datasets(self):
        pass

    def save_dataset(self, df):
        if self.to_json:
            output_name = self.output_name + '.json'
            df.to_json(join(self.loc_data, output_name),
                       default_handler=str, orient='records')
            return None

        output_name = self.output_name + '.csv'
        df.to_csv(join(self.loc_data, output_name))
