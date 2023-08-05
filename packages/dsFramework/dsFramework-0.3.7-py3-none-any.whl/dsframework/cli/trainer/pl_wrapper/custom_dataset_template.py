from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, pytorch lightning 'Dataset' base class. Implement for external datasets.
class generatedClass(ZIDS_PLCustomDataset):
    """! Template for loading an external custom dataset

    Pytorch lightning docs:
    https://pytorch.org/docs/stable/data.html#torch.utils.data.Dataset
    https://pytorch-lightning.readthedocs.io/en/stable/notebooks/course_UvA-DL/01-introduction-to-pytorch.html?highlight=__getitem__#The-dataset-classs

    """
    def __init__(self, x_ds, y_ds):
        """! Initializer for a custom dataset creation

            Args:
                x_ds: Dataset
                y_ds: Labels for dataset.

            Important note:
                In ZIDSCustomDataset base class there is an implementation of __getitem__ and __len__, which
                are essential for creating a custom Dataset.

        """
        super().__init__(x_ds, y_ds)

    def __len__(self):
        return len(self.y_data)

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]
