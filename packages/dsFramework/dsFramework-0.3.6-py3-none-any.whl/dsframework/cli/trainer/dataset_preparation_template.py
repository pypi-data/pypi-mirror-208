class generatedClass:

    def __init__(self, dataset_path='', save_datasets=False, save_path='', dataset_config=None):
        self.dataset_path = dataset_path
        self.save_datasets = save_datasets
        self.save_path = save_path
        self.dataset_config = dataset_config
        self.dataset_df = self._read_dataset(dataset_path)

    def prepare_datasets(self):
        """ Do here all dataset preparation for splitting.

        Example:

            if self.save_datasets:
                with open(self.save_path + '/train_dataset.pickle', 'wb') as pickle_file:
                    pickle.dump(x_train_data, pickle_file)
                with open(self.save_path + '/test_dataset.pickle', 'wb') as pickle_file:
                    pickle.dump(x_test_data, pickle_file)
                with open(self.save_path + '/val_dataset.pickle', 'wb') as pickle_file:
                    pickle.dump(x_val_data, pickle_file)
                return
                    self.save_path + '/train_dataset.pickle',
                    self.save_path + '/val_dataset.pickle',
                    self.save_path + '/test_dataset.pickle'

            else:
                return pickle.dumps(x_train_data), pickle.dumps(x_val_data), pickle.dumps(x_test_data)


        """

        train_dataset_path = self.save_path + '/train_dataset.pickle'
        val_dataset_path = self.save_path + '/val_dataset.pickle'
        test_dataset_path = self.save_path + '/test_dataset.pickle'

        return train_dataset_path, val_dataset_path, test_dataset_path

    def _read_dataset(self, dataset_path):
        """Reads the full dataset.

        Example:
            dataset_df = pd.read_csv(self.dataset_path)
        """

        dataset_df = None

        return dataset_df
