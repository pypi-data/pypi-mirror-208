import os

from dsframework.base.trainer.pl_wrapper import *


class ToOnnx:
    def __init__(self, model_config=None):

        self.model_config = model_config
        self.input_length = 0  # size of the input length.

    def save_checkpoint_as_onnx(self, checkpoint_path, pl_model_class):
        success = True
        try:
            model = self.load_model(checkpoint_path, pl_model_class)

            if self.input_length == 0:
                self.input_length = model._modules['0'].in_features  # set input length here

            input_ids, att_masks = self.generate_random_int_ids(self.input_length)

            save_to = os.path.splitext(checkpoint_path)[0] + '.onnx'
            success = self.save_to_onnx(model, save_to, input_ids, att_masks)

        except Exception as ex:
            print(f'Exception in save_checkpoint_as_onnx: {ex}')

        return success

    def load_model(self, checkpoint_path, pl_model_class):

        checkpoint_model = pl_model_class.load_from_checkpoint(
            checkpoint_path, strict=False,
            model_config=self.model_config,
            metrics_config=None,
            trainer_config=None)

        model = checkpoint_model.model.to(self.model_config.get('device', 'cpu'))
        model.eval()

        return model

    def generate_random_int_ids(self, input_length, range_from=0, range_to=3000):

        input_ids = torch.randint(range_from, range_to, (1, input_length), requires_grad=False)  # Simulates the input_ids
        att_masks = torch.randint(0, 2, (1, input_length), requires_grad=False)

        return input_ids, att_masks

    def save_to_onnx(self, model, save_to_path, input_ids, attention_mask):

        success = True

        try:
            torch.onnx.export(
                model,  # model being run
                (input_ids, attention_mask),  # model input (or a tuple for multiple inputs)
                save_to_path,  # where to save the model (can be a file or file-like object)
                export_params=True,  # store the trained parameter weights inside the model file
                opset_version=12,  # the ONNX version to export the model to -  recommended - the latest version
                do_constant_folding=True,  # whether to execute constant folding for optimization
                input_names=['input_ids', 'attention_mask'],  # the model's input names
                output_names=['output'],  # ,  # the model's output names
                dynamic_axes={'input_ids': {0: 'batch_size', 1: 'seq_len'},  # variable length axes
                              'attention_mask': {0: 'batch_size', 1: 'seq_len'},
                              'output': {0: 'batch_size'}})
        except Exception as ex:
            print(f'exception saving onnx: {ex}')
            success = False

        return success
