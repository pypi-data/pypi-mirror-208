from itertools import cycle
from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, pytorch lightning 'IterableDataset' base class. Implement for external datasets.
class generatedClass(ZIDSIterableDataset):
    """! This is the template class for iterable datasets,
    It basically returns the dataset records by batch.

    Pytorch lightning docs:
    https://pytorch-lightning.readthedocs.io/en/latest/guides/data.html?highlight=IterableDataset
    https://pytorch-lightning.readthedocs.io/en/latest/guides/data.html?highlight=IterableDataset#iterable-datasets
    https://pytorch-lightning.readthedocs.io/en/latest/clouds/fault_tolerant_training_faq.html?highlight=IterableDataset#how-do-i-use-iterable-datasets
    https://pytorch.org/docs/stable/data.html#torch.utils.data.IterableDataset

    Usage:
        override __iter__ method.

    """

    def __init__(self, data):
        self.data_source = data

    def process_data(self, data):
        """Yields a 'rec' out of the dataset."""
        for rec in data:
            yield rec

    def get_stream(self, data):
        """Cycles through dataset and calls process_data method.
        Sending batches can be implemented here."""
        return cycle(self.process_data(data))

    def __iter__(self):
        return self.get_stream(self.data_source)


def worker_init_fn():
    worker_info = get_worker_info()
    dataset = worker_info.dataset  # the dataset copy in this worker process
    worker_id = worker_info.id
    split_size = len(dataset.data) // worker_info.num_workers
    dataset.data = dataset.data[worker_id * split_size:(worker_id + 1) * split_size]
