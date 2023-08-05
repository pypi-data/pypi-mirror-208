from os.path import exists
from typing import Optional, Union, Any
import csv
from dsframework.base.trainer.pl_wrapper import *


class ZIDS_PLDataModule(pl.LightningDataModule):
    """! This class inherits from LightningDataModule"""

    def __init__(self,
                 model_config=None,
                 train_set: Dataset = None,
                 val_set: Dataset = None,
                 test_set: Dataset = None):
        """! Define required parameters here."""
        super().__init__()

        self.train_val_len = 0
        self.train_val_set = train_set
        self.val_set = val_set
        self.train_set = None if val_set is None else train_set
        self.test_set = test_set
        self.predict_set = None
        self.batch_size = model_config['batch_size']
        self.num_workers = model_config['num_workers']

    def prepare_data(self):
        """! Define steps that should be done on only one GPU, like getting data."""
        pass

    def setup(self, stage: Optional[str] = None) -> None:
        """! Make assignments here (val/train/test split)
        called on every process in DDP
        Define steps that should be done on
        every GPU, like splitting data, applying
        transform etc.


        Example:
            @code
            # Assign train/val datasets for use in dataloaders:
            if stage in (None, "fit"):
                mnist_full = MNIST(self.data_dir, train=True, transform=self.transform)
                self.ds_train, self.ds_val = random_split(mnist_full, [55000, 5000])

            # Assign test dataset for use in dataloader(s):
            if stage in (None, "test"):
                self.ds_test = MNIST(self.data_dir, train=False, transform=self.transform)

            @endcode
        """
        pass

    def train_dataloader(self) -> TRAIN_DATALOADERS:
        """! Return DataLoader for Training Data here

        Example:
            @code
            train_split = Dataset(...)
            return DataLoader(train_split)
            @endcode
        """
        return DataLoader(self.train_set, batch_size=self.batch_size, num_workers=self.num_workers)

    def val_dataloader(self) -> EVAL_DATALOADERS:
        """! Return DataLoader for data validation.

        Example:
            @code
            val_split = Dataset(...)
            return DataLoader(val_split)
            @endcode
        """
        return DataLoader(self.val_set, batch_size=self.batch_size, num_workers=self.num_workers)

    def test_dataloader(self) -> EVAL_DATALOADERS:
        """! Return DataLoader for data testing.

        Example:
            @code
            val_split = Dataset(...)
            return DataLoader(test_split)
            @endcode
        """
        return DataLoader(self.test_set, batch_size=self.batch_size, num_workers=self.num_workers)

    def predict_dataloader(self) -> EVAL_DATALOADERS:
        return DataLoader(self.predict_set, batch_size=self.batch_size)

    def teardown(self, stage: Optional[str] = None) -> None:
        """! Called at the end of fit(train + validate), validate, test, or predict.
            called on every process in DDP
        """
        pass

    def load_dataset(self, file_path, file_type):
        """! Loads an external dataset, NOT FINISHED YET."""

        if file_type == 'csv':
            with open(file_path) as csv_file:
                self.train_val_set = list(csv.reader(csv_file))

        return self.train_val_set

    def parse_dataset(self, remove_header) -> Union[Any, Any]:
        """! Parse your data here, it needs to return x, y.
            Returns:
                x: dataset
                y: target

        Example:
            @code{.py}
            if remove_header:
                self.dataset = self.dataset[1:]

            x = np.array(self.dataset, dtype=np.float32)[:, :-1]
            y = np.array(self.dataset, dtype=np.float32)[:, -1].reshape(-1, 1)

            return x, y
            @endcode
        """
        raise Exception("Not implemented exception (parse_dataset).")
