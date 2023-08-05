import os
from enum import Enum
from typing import Union, List

import pandas
import matplotlib.pyplot as plt
import seaborn as sn

from dsframework.base.trainer.pl_wrapper import *
from trainer.pl_wrapper.network_module import generatedProjectNameNetworkModule

##
# @file
# @brief generatedClass class, based on pytorch lightning 'LightningModule' base class.


class ActionType(Enum):
    TRAINING = 'train'
    VALIDATION = 'val'
    TESTING = 'test'


class StepEpoch(Enum):
    STEP = 'step',
    EPOCH = 'epoch'


class generatedClass(ZIDS_PLModel):
    """! Model template class inherits from ZIDSModel(LightningModule), which organizes your code into 6 sections:

        - Computations (init).
        - Train Loop (training_step)
        - Validation Loop (validation_step)
        - Test Loop(test_step)
        - Prediction Loop (predict_step)
        - Optimizers and LR Schedulers(configure_optimizers)

        Log parameters:
        - For single value, use:
            self.log("test_loss", test_loss)  # prog_bar=True

        - For multiple values use dictionary, use:
            values = {"loss": loss, "acc": acc, "metric_n": metric_n}  # add more items if needed
            self.log_dict(values)

        View results in tensorboard:
            tensorboard --logdir=lightning_logs/

        Loading datasets:

            example:
            @code{.py}
            train_set = datasets.MNIST(os.getcwd() + '/data', download=True, train=True, transform=transform)
            test_set = datasets.MNIST(os.getcwd() + '/data', download=True, train=False, transform=transform)

            # use 20% of training data for validation
            train_set_size = int(len(train_set) * 0.8)
            valid_set_size = len(train_set) - train_set_size

            # split the train set into two
            seed = torch.Generator().manual_seed(42)
            train_set, valid_set = random_split(train_set, [train_set_size, valid_set_size], generator=seed)

            train_set_loader = DataLoader(train_set, num_workers=2)
            val_set_loader = DataLoader(valid_set, num_workers=2)
            test_set_loader = DataLoader(test_set, num_workers=2)
            @endcode


        Training:
            example:
            @code{.py}
            trainer = pl.Trainer(max_epochs=1, callbacks=[checkpoint_callback])
            trainer.fit(model=autoencoder, train_dataloaders=train_set_loader, val_dataloaders=val_set_loader)
            @endcode

        Testing:
            example:
            @code{.py}
            trainer.test(model=autoencoder, dataloaders=test_set_loader)
            @endcode

        Loading a trained model, use:
            - load_from_checkpoint

                example:
                @code{.py}
                model = MyTrainer.load_from_checkpoint('lightning_logs/epoch=0-step=48000.ckpt')
                @endcode


        Saving a model, use:
            - save_checkpoint

                for example:
                @code{.py}
                trainer.save_checkpoint("my_checkpoint.ckpt")
                @endcode

            - ModelCheckpoint - define automated checkpoint saving, use:
                for example:
                @code{.py}
                checkpoint_callback = ModelCheckpoint(dirpath="lightning_logs/", save_top_k=2, monitor="val_loss")
                @endcode


    """
    def __init__(self, model_config=None, metrics_config=None, trainer_config=None, save_path=''):
        """! Model class initializer, receives the network and loss function, it initializes all parameter to be
        tracked. """
        super().__init__(model_config, metrics_config, trainer_config)
        self.test_conf_mat = None

        self.model, self.tokenizer = generatedProjectNameNetworkModule.load_define_model()
        self.batch_size = self.model_config.get('batch_size', 32)
        self.num_classes = self.model_config.get('num_classes', None)
        self.learn_rate = self.model_config.get('learning_rate', 1e-3)

        self._device = self.model_config.get('device', 'cpu')
        self.test_results = None
        self.save_path = save_path

        if self.metrics:
            self.initialize_metrics()

        # self.save_hyperparameters()

    def configure_optimizers(self):
        """! Choose what optimizers and learning-rate schedulers to use in your optimization. Normally you’d need one.
                But in the case of GANs or similar you might have multiple.

                    Returns: Any of this 6 options
                        - Single optimizer.
                        - List or Tuple of optimizers.
                        - Two lists - The first list has multiple optimizers, and the second has multiple LR schedulers
                            (or multiple lr_scheduler_config).
                        - Dictionary, with an "optimizer" key, and (optionally) a "lr_scheduler" key whose value
                            is a single LR scheduler or lr_scheduler_config.
                        - Tuple of dictionaries as described above, with an optional "frequency" key.
                        - None - Fit will run without any optimizer.

                Example:
                    @code{.py}
                    optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
                    return optimizer
                    @endcode

                Another example:
                    @code{.py}
                    SGD_optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.7)
                    return SGD_optimizer
                    @endcode

        """
        optimizer = Optimizers.Adam(self.parameters(), lr=self.learn_rate)

        scheduler = transformers.get_scheduler(
            "linear",
            optimizer=optimizer,
            num_warmup_steps=self.model_config['num_warmup_steps'],
            num_training_steps=self.trainer.estimated_stepping_batches
        )

        return [optimizer], [scheduler]

    def forward(self, x):
        """! Defines the computation performed at every call.

        Implementation example:
            @code{.py}
            x = x.view(x.size(0), -1)
            x = self.nnetwork(x)
            return x
            @endcode
        """
        pass

    def training_step(self, batch, batch_idx):
        """! Override to enable training loop

        Implementation example:
            @code{.py}
            def training_step(self, batch, batch_idx):
                x, y = batch
                x = x.view(x.size(0), -1)
                z = self.encoder(x)
                x_hat = self.decoder(z)
                loss = function.mse_loss(x_hat, x)
                return loss
            @endcode

        If you need to do something with all the outputs of each training_step(), override the
        training_epoch_end() method.
        """
        loss, labels, predictions = self.do_step(batch)

        self.log_metrics(predictions, labels, ActionType.TRAINING, StepEpoch.STEP)
        self.log("train_loss", loss, prog_bar=True, logger=True, on_step=False, on_epoch=True,
                 batch_size=self.batch_size)

        return loss

    def validation_step(self, batch, batch_idx):
        """! Override to enable validation loop

        Implementation example:
            @code{.py}
            def validation_step(self, batch, batch_idx):
                x, y = batch
                x = x.view(x.size(0), -1)
                z = self.encoder(x)
                x_hat = self.decoder(z)
                test_loss = function.mse_loss(x_hat, x)
                self.log("val_loss", test_loss, prog_bar=True)
            @endcode
        """
        loss, labels, predictions = self.do_step(batch)

        self.log_metrics(predictions, labels, ActionType.VALIDATION, StepEpoch.STEP)
        self.log("val_loss", loss, batch_size=self.batch_size)

        return {'loss': loss, 'labels': labels, 'predictions': predictions}

    def validation_epoch_end(self, outputs: Union[EPOCH_OUTPUT, List[EPOCH_OUTPUT]]) -> None:

        labels, preds = self.prepare_results(outputs)

        confusion_matrix = self.val_confusion_matrix(preds, labels)

        self._save_log_conf_mat_image(confusion_matrix, self.current_epoch, self.save_path,
                                      self.model_config['label_names'])

        self._save_report(confusion_matrix, self.current_epoch, self.save_path, self.model_config['label_names'])

    def test_step(self, batch, batch_idx):
        """! Override to enable test loop.

        Implementation example:
            @code{.py}
            x, y = batch
            x = x.view(x.size(0), -1)
            z = self.encoder(x)
            x_hat = self.decoder(z)
            test_loss = function.mse_loss(x_hat, x)
            self.log("test_loss", test_loss)  # prog_bar=True

            return {'loss': loss, 'preds': pred, 'target': y}  # will be available in test_epoch_end
            @endcode
        """
        loss, labels, predictions = self.do_step(batch)

        self.log_metrics(predictions, labels, ActionType.TESTING, StepEpoch.STEP)

        self.log("test_loss", loss, batch_size=self.batch_size)

        return {'loss': loss, 'labels': labels, 'predictions': predictions}

    def test_epoch_end(self, outputs):
        """! Implement this to calculate test results and fill the local dictionary return self.test_results

            Args:
                outputs: Array (ie. dict, list etc.) with accumulated results returned from:
                 def test_step(self, batch, batch_idx)

        Confusion matrix example:
            preds = torch.cat([tmp['preds'] for tmp in outputs])
            targets = torch.cat([tmp['target'] for tmp in outputs])

            conf_matrix_results = self.confusion_matrix(preds, targets)

        Results structure example:
            self.test_results = {
                'precision': precision_result,
                'accuracy': accuracy_result,
                'recall': recall_result,
                'f1': f1_result,
                'confusion_matrix': conf_matrix_results}

        """
        labels, preds = self.prepare_results(outputs)

        self.test_conf_mat = self.test_confusion_matrix(preds, labels)

        self._save_log_conf_mat_image(self.test_conf_mat, -1, self.save_path, self.model_config['label_names'])
        self._save_report(self.test_conf_mat, -1, self.save_path, self.model_config['label_names'])

        self.test_results = self.prepare_test_results()

    def log_metrics(self, pred=None, y=None, step_name: ActionType = ActionType.TRAINING,
                    step_epoch: StepEpoch = StepEpoch.STEP):
        """Log the metrics specified in config.py metrics section."""

        for key in self.metrics:

            if key == 'confusion_matrix':
                continue

            if not self.metrics[key]:
                continue

            prog_bar = True if key != 'confusion_matrix' else False

            method_name = "%s_%s" % (ActionType[step_name.name].value, key)

            try:
                metric_method = getattr(self, method_name)
            except AttributeError as e:
                print(f'No method {method_name} metric found, exception: {e}.')
                return

            if step_epoch == StepEpoch.STEP:
                metric_method(pred, y)
                self.log(f'{method_name}', metric_method, prog_bar=prog_bar, on_step=False, on_epoch=True,
                         batch_size=self.batch_size)
            else:
                self.log(f'{method_name}_epoch', metric_method, prog_bar=prog_bar, on_step=False, on_epoch=True,
                         batch_size=self.batch_size)

    def prepare_test_results(self):
        """Prepare test results' dictionary with configured metrics."""
        test_results = {}

        for key in self.metrics:

            if key == 'confusion_matrix':
                test_results[key] = self.test_conf_mat
                continue

            if not self.metrics[key]:
                continue

            method_name = "%s_%s" % ('test', key)
            metric_method = getattr(self, method_name)
            test_results[key] = metric_method.compute()

        return test_results

    def get_test_results(self):
        """Returns test_results."""
        if self.test_results:
            return self.test_results
        else:
            return None

    def do_step(self, batch):

        input_ids = batch[0].to(self._device)
        # input_mask = batch[1].to(self._device)
        input_labels = batch[1].to(self._device)
        input_ids = input_ids.view(input_ids.size(0), -1)
        logits = self.model(input_ids)

        loss = self.loss_function(logits, input_labels)

        labels = input_labels.view(-1)
        predictions = torch.argmax(logits, dim=1)

        return loss, labels, predictions

    def prepare_results(self, outputs):

        preds = torch.cat([tmp['predictions'] for tmp in outputs])
        labels = torch.cat([tmp['labels'] for tmp in outputs])

        return labels, preds

    def _save_log_conf_mat_image(self, confusion_matrix, current_epoch, save_path, label_names=None):

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        title = f'Confusion matrix, epoch: {current_epoch}' if current_epoch != -1 else f'Confusion matrix - test'
        image_name = f'conf_mat_{current_epoch}.png' if current_epoch != -1 else 'conf_mat_test.png'

        if label_names is None:
            df_conf_mat = pandas.DataFrame(confusion_matrix.numpy())
        else:
            df_conf_mat = pandas.DataFrame(confusion_matrix.numpy(), index=label_names, columns=label_names)

        plt.figure(figsize=(10, 7))
        plt.title(title)
        cm = sn.heatmap(df_conf_mat, annot=True, fmt='d')
        figure = cm.get_figure()
        figure.savefig(os.path.join(save_path, image_name))
        plt.close()

        self.trainer_config['logger'].experiment.add_figure("Confusion matrix", figure, self.current_epoch)

    def _save_report(self, confusion_matrix, current_epoch, save_path, label_names=None):

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_name = f'metrics_report_{current_epoch}.text' if current_epoch != -1 else 'metrics_report.text'
        file_name = os.path.join(save_path, file_name)

        report_string = f'\nEpoch: {current_epoch}\n' \
                        f'Confusion Matrix:\n{confusion_matrix}\n'
        if label_names:
            report_string = report_string + f'Number of Tokens:\n{len(label_names)}\n'

        with open(file_name, "a") as f:
            f.write(report_string)

    def initialize_metrics(self):

        average = self.metrics.get('average', 'micro')

        for key in self.metrics:
            if not self.metrics[key]:
                continue

            if key == 'accuracy':
                self.train_accuracy = torchmetrics.Accuracy(average=average, num_classes=self.num_classes)
                self.val_accuracy = torchmetrics.Accuracy(average=average, num_classes=self.num_classes)
                self.test_accuracy = torchmetrics.Accuracy(average=average, num_classes=self.num_classes)
            elif key == 'precision':
                self.train_precision = torchmetrics.Precision(average=average, num_classes=self.num_classes)
                self.val_precision = torchmetrics.Precision(average=average, num_classes=self.num_classes)
                self.test_precision = torchmetrics.Precision(average=average, num_classes=self.num_classes)
            elif key == 'recall':
                self.train_recall = torchmetrics.Recall(average=average, num_classes=self.num_classes)
                self.val_recall = torchmetrics.Recall(average=average, num_classes=self.num_classes)
                self.test_recall = torchmetrics.Recall(average=average, num_classes=self.num_classes)
            elif key == 'f1':
                self.train_f1 = torchmetrics.F1Score(average=average, num_classes=self.num_classes)
                self.val_f1 = torchmetrics.F1Score(average=average, num_classes=self.num_classes)
                self.test_f1 = torchmetrics.F1Score(average=average, num_classes=self.num_classes)
            elif key == 'confusion_matrix':
                if not self.model_config['num_classes_conf_mat']:
                    raise Exception(
                        "To use confusion matrix metric, please set 'num_classes_conf_mat' parameter in config.py.")
                self.train_confusion_matrix = torchmetrics.ConfusionMatrix(
                    num_classes=self.model_config['num_classes_conf_mat'])
                self.val_confusion_matrix = torchmetrics.ConfusionMatrix(
                    num_classes=self.model_config['num_classes_conf_mat'])
                self.test_confusion_matrix = torchmetrics.ConfusionMatrix(
                    num_classes=self.model_config['num_classes_conf_mat'])

