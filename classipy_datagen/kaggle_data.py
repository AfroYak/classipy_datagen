from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import glob
import os
import shutil
from os.path import normpath, join, abspath, dirname

from .data_generator import DataGenerator


class KaggleDataset(DataGenerator):
    def __init__(
        self, n_datasets=100, max_size=25_000_000, n_samples=1000, 
        output_name="kaggle_data", datset_names=None, to_json=True, page=4
        ) -> None:
        super().__init__(n_samples=n_samples, n_datasets=n_datasets,
                         output_name=output_name, to_json=to_json)

        # Kaggle Specific Parameters
        self.dataset_names = datset_names
        self.max_size = max_size
        self.page = page
        self.api = KaggleApi()
        self.api.authenticate()

        self.loc_temp_data = join(self.loc_data, 'temp_datasets')

    def get_dataset_names(self):
        dataset_names = []
        dataset_num = 0
        while dataset_num < self.n_datasets:
            try:
                resp = self.api.datasets_list(
                    page=self.page,
                    filetype="csv",
                    max_size=self.max_size
                )

                for i in range(20):  # TODO FIX THIS
                    dataset_names.append(
                        (resp[i]["id"], resp[i]["ref"], resp[i]["totalBytes"])
                    )
                    dataset_num += 1
                    if dataset_num >= self.n_datasets:
                        break
                self.page += 1

            except IndexError as e:
                break

        self.dataset_names = pd.DataFrame(
            dataset_names,
            columns=["id", "ref", "size"],
        )
        self.dataset_names.to_csv(join(self.loc_data, "name_data_sets.csv"))

    def download_datasets(self):
        if not isinstance(self.dataset_names, pd.DataFrame):
            self.get_dataset_names()

        all_dataframes = []

        for dataset_name in self.dataset_names["ref"]:
            self.api.dataset_download_files(
                dataset_name, self.loc_temp_data, unzip=True
            )

            dataset_file_names = self.read_filenames()
            dataset_dataframes = self.read_data_frame(
                dataset_file_names, dataset_name)
            all_dataframes += dataset_dataframes

            # print('Clean-up | ', dataset_name)
            self.clean_tempfolder()

            df_all = pd.concat(all_dataframes, axis=0).reset_index(
                drop=True)
            self.save_dataset(df_all)

        print(
            f'Completed Creating Dataset | Saved @ {join(self.loc_data,self.output_name)}')

        return df_all

    def read_filenames(self):
        return [
            name
            for name in
            glob.glob(self.loc_temp_data + "/**/*.csv", recursive=True)]

    def clean_tempfolder(self):
        for file in glob.glob(self.loc_temp_data+"/*"):
            try:
                os.remove(file)
            except OSError:
                shutil.rmtree(file, ignore_errors=True)

    def read_data_frame(self, file_names, dataset_name):
        count_passes = 0
        data_frames = []
        for file_name in file_names:
            *_, table_name = file_name.rpartition('/')

            try:
                df = pd.read_csv(file_name)
                df_calc = self.get_dataframe(
                    df, dataset_name, table_name)
            except Exception as e:
                count_passes += 1
                print('ERROR: SKIPPING CSV:', dataset_name, table_name, type(e))
                df_calc = pd.DataFrame()
            finally:
                data_frames.append(df_calc)

            print(f'Completed :', {dataset_name}, {table_name})

        return data_frames


if __name__ == "__main__":
    k = KaggleDataset(3)
    k.download_datasets()
    print('DONE!!')
    pass
