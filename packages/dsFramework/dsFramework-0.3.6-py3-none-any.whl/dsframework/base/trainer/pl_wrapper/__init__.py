# ======= Torch imports =========
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, IterableDataset, random_split, get_worker_info
import torchmetrics
import transformers
from torchvision import transforms, datasets
import pytorch_lightning as pl
from pytorch_lightning import Callback
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning.loggers import LightningLoggerBase, TensorBoardLogger
from pytorch_lightning.accelerators import Accelerator
from pytorch_lightning.profiler import BaseProfiler
from pytorch_lightning.strategies import Strategy
from pytorch_lightning.plugins import PLUGIN_INPUT
from pytorch_lightning.utilities.types import (
    STEP_OUTPUT,
    EPOCH_OUTPUT,
    EVAL_DATALOADERS,
    TRAIN_DATALOADERS
)

# ======== DSF imports ========
from dsframework.base.trainer.pl_wrapper.optimizers import Optimizers
from dsframework.base.trainer.pl_wrapper.model.plmodel import ZIDS_PLModel
from dsframework.base.trainer.pl_wrapper.torch_module import ModuleBase
from dsframework.base.trainer.pl_wrapper.data.data_module import ZIDS_PLDataModule
from dsframework.base.trainer.pl_wrapper.data.custom_dataset import ZIDS_PLCustomDataset
from dsframework.base.trainer.pl_wrapper.data.iterable_dataset import ZIDSIterableDataset
from dsframework.base.trainer.pl_wrapper.model.nnetwork import ZIDSNetwork

# tensorboard --logdir=dsframework/cli/trainer/lightning_logs
