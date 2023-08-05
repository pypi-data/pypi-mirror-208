## Trainer tutorial {#trainer1}

This tutorial will guide you through using the trainer support in dsf.
It is mainly a structure that even-though is oriented towards pytorch lightning, it can incorporate other technologies.

### Prerequisites installation:
pip install -r requirements_docker.txt
dsf-cli install-trainer-packages


### Components:
All components are located in the 'trainer/', folder.

| File name               | Description                                                   | Related Pytorch lightning class | 
|-------------------------|---------------------------------------------------------------|---------------------------------|
| main.py                 | main entry point - Start here                                 | NA                              |
| data.py                 | datasets functionality                                        | pl.LightningDataModule          |
| model.py                | model related func., network definition, load from pretrained | pl.LightningModule              |
| train.py                | executes training                                             | pl.Trainer.fit                  |
| test.py                 | executes test on test dataset                                 | pl.Trainer.test                 |
| config.py               | configurations                                                | ModelCheckpoint, EarlyStopping  |
| comparison.py           | compare test results with evaluation results.                 | NA                              |
| dataset_preparation.py  | prepare datasets for training, validation and test            | NA                              |


###Data - data.py
Located in data.py file and its main job is holding the datasets and all functionality related to the datasets.

For the trainer it needs to keep a train and validation datasets.
For the test process it needs a test dataset.

Implement the method create_data_module() to return a data module that includes the 3 datasets.

Example if using pytorch lightning, <project>DataModule based on pl.LightningDataModule class:

    self.data_module = <project>DataModule(
        model_config=self.model_config,
        train_set=self.dataset_train,
        val_set=self.dataset_validation,
        test_set=self.dataset_test
    )

    return self.data_module

Important note:
a split() method that needs to be implemented, to split the dataset to train validation and test.
Surprisingly it is located in the main.py initializer, because it is a shared class between the 
train and test processes. 
The class dataset_prepare.py can be used to place methods used to prepare and split the dataset.

###Model - model.py
Holds all model related functionality such as network definition, loss function to use, load from pretrained model etc.

Implement define_model() method to create a model class to be used in the train/fit process.

Example (pytorch lightning), <project>Plmodel based on pl.LightningModule class:

    self.model = <project>Plmodel(
        model_config=self.model_config,
                metrics_config=self.metrics_config,
                trainer_config=self.trainer_config,
                save_path=self.save_path
    )

Network creation/loading located in trainer/pl_wrapper/network_module.py

Example (pytorch lightning):

    nnetwork = nn.Sequential(
        nn.Linear(28 * 28, 64),
        nn.ReLU(),
        nn.Linear(64, 3),
        nn.Linear(3, 64),
        nn.ReLU(),
        nn.Linear(64, 28 * 28)
    )

And / Or:

    self.bert = BertModel.from_pretrained("bert-base-cased")

And / Or:
    model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=6)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

###Train - train.py
Create the trainer module and executes the actual training.

Implement execute() method to create a trainer class to be used in the train/fit process.

The trainer class requires the following to run:
- data_module - Implementation of pl.LightningDataModule with a train and validation datasets, or use our implemented 
pytorch lightning wrapper, located in trainer/pl_wrapper/data_module.py, called <project>DataModule.
- model - Implementation of pl.LightningModule, or use our predefined class located in trainer/pl_wrapper/plmodule.py,
called <project>Plmodel.
- pl.Trainer - instantiated with 'trainer_config'

The trainer basically executes trainer.fit, see the following example (pytorch lightning):

    self.trainer = pl.Trainer(**self.trainer_config)
    self.trainer.fit(self.model, self.data_module)

This class also saves the last model (if implemented), which is important to note - doesn't mean it is the best model. 
If using pytorch lightning, use ModelCheckpoint callback to save the best model, callback defined in config.py.

###Configuration - config.py
Configuration of:
Pytorch lightning checkpoint callback - ModelCheckpoint
Pytorch lightning early stopping callback - EarlyStopping

'model_config' - Model configuration, add additional keys if required.
'trainer_config' - Transferred to pytorch lightning pl.Trainer as is, add only supported trainer parameters.
'dataset_config' - Dataset configuration, add additional keys if required.
'metrics' - set to True the required metric results.

###Test - test.py
Its main job is to execute a test of the model using a test dataset. The difference between a test and a regular 
prediction, is that it is done on a labeled dataset which was never introduced to the model.

To run the test using pytorch lightning, it requires:
- data_module - Implementation of pl.LightningDataModule with a test dataset, or use our implemented pytorch lightning 
wrapper, located in trainer/pl_wrapper/data_module.py, called <project>DataModule.
- model - Implementation of pl.LightningModule, or use our predefined class located in trainer/pl_wrapper/plmodule.py,
called <project>Plmodel.
- pl.Trainer - instantiated with 'trainer_config'

The test basically executes trainer.test, see the following example:

    self.trainer = pl.Trainer(**trainer_config)
    self.trainer.test(self.model, self.data_module)

###Comparison - compare.py
The main job of this class is to compare results of:
- Current model running on the test dataset.
- an existing model, by running the same test dataset on its evaluation function.

The compare() method needs to be implemented, a suggested implementation exists in the code for creating a dictionary 
of each metrics (defined in config), for both the trained and evaluation results.

Example:

    if self.test_results is None or self.eval_results is None:
        return "No test results found."

    self.comparison_results = {
        metric: {'trained': self.test_results[metric], 'eval': self.eval_results[metric]}
        for metric in self.metrics
        if metric in self.test_results and metric in self.eval_results and self.metrics[metric]}

    return self.comparison_results

It looks something like this:

    comparison_results = {
            'precision': {'trained': tensor(0.8828), 'eval': 1.1}, 
            'accuracy': {'trained': tensor(0.8828), 'eval': 1.2}, 
            'recall': {'trained': tensor(0.8828), 'eval': 1.3}, 
            'f1': {'trained': tensor(0.8828), 'eval': 1.4}, 
            'confusion_matrix': {
                'trained': {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0},
                'eval': {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}
    }

### Main - trainer_main.py
This file is where everything happens scroll down to the bottom to see the implementation.

Run this file to execute:

Training:

    main_class = Main(cfg=config, dataset_path=None)
    main_class.execute_trainer()

Test:

    main_class_test = Main(cfg=config, test_dataset_path=None)
    test_results = main_class_test.execute_test(model_path=model_path)

Evaluation:
    main_class_eval = Main(cfg=config, test_dataset_path=None)
    eval_results = main_class_eval.execute_eval()

Comparison:

    comparison_results = <project>Comparison(
        test_results=test_results,
        eval_results=eval_results,
        metrics_config=config['metrics']).compare()
