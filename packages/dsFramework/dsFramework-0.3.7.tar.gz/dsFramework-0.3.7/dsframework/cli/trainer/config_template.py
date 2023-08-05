import os
from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief config.py, holds all configurations in dictionary format.

## ModelCheckpoint - pytorch lightning auto save callback.
checkpoint_callback = ModelCheckpoint(
    save_top_k=1,
    save_last=True,
    monitor="val_loss",
    mode="min",
    filename="my-chkpnt-{epoch:02d}-{val_loss:.2f}",
)

## EarlyStopping - pytorch lightning early stopping callback.
early_stopping_callback = EarlyStopping(
    monitor='val_loss',
    patience=10,  # number of val checks with no improvement
    mode='max'
)

## Supported loggers by pytorch lightning:
## TensorBoardLogger, MLFlowLogger, NeptuneLogger, WandbLogger, CometLogger, CSVLogger.
# By default created the TensorBoardLogger and it is the only one tested.
# More information here: https://pytorch-lightning.readthedocs.io/en/stable/extensions/logging.html
pl_logger = TensorBoardLogger(save_dir=os.getcwd(), version=f'v', name='training_output')
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

## Configurations, can add or remove parameters with two exception: metrics and the trainer_config is the exact parameters
## the pytorch lightning trainer class accepts, it is used: pl.Trainer(**config['trainer_config'])
config = {
    'model_config': {
        'learning_rate': 1e-3,
        'loss_function': F.cross_entropy,
        'batch_size': 32,
        'num_classes': None,
        'num_classes_conf_mat': None,
        'label_names': None,
        'num_workers': 1,
        'seed': 42,
        'save_last_model': False,
        'model_name': 'my_model.ckpt',
        'device': device,
        'num_warmup_steps': 0,
        'save_checkpoint_as_onnx': False,
        'average': 'micro'  # 'macro'
    },
    'trainer_config': {  # Do not change, training_config is dedicated to pytorch lighting trainer module and uses its exact params.
        'max_epochs': 1,
        'accelerator': None,  # 'cpu', 'gpu', 'tpu', 'ipu', 'auto', None
        'devices': None,  # number of accelerators: -1-all, 1, 3, 4...8, None, [1, 3]-gpu ids, None
        'strategy': None,  # 'dp', 'ddp', 'ddp2', 'ddp_spawn'
        'num_processes': None,  # number of cpus
        'enable_checkpointing': True,
        'default_root_dir': './',  # root dir to save checkpoints
        'callbacks': [checkpoint_callback],
        'enable_progress_bar': True,  # PRD - for production change to False
        'log_every_n_steps': 20,
        'logger': pl_logger,
        'num_sanity_val_steps': 0  # =0 will not perform sanity test.
    },
    'metrics': {  # works with pytorch lightning and will calculate and return the specified metrics.
        'precision': True,
        'accuracy': True,
        'recall': True,
        'f1': True,
        'confusion_matrix': True
    },
    'dataset_config': {
        'save_dataset': True,
        'train_ratio': 0.75,
        'validation_ratio': 0.15,
        'test_ratio': 0.10
    }
}
