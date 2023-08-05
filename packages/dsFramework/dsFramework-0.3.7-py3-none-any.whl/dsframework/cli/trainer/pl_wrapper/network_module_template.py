from typing import Any

from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, define neural network layers.
class generatedClass(ZIDSNetwork):
    """! Define your networks here, or load from pretrained model.

    for example:
        @code
        model = nn.Sequential(
            nn.Linear(28 * 28, 64),
            nn.ReLU(),
            nn.Linear(64, 3),
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 28 * 28)
        )
        @endcode

    Another example:
        @code
        nnetwork_wine = nn.Sequential(
        nn.Linear(11, 1),
        nn.ReLU(),
        nn.Linear(1, 1))
        @endcode

    Another example:
        @code
        self.bert = BertModel.from_pretrained("bert-base-cased")
        @endcode
    """

    model = None

    def __init__(self):
        super().__init__(self.model)

    @staticmethod
    def load_define_model():
        """Load the model and tokenizer here, called from pytorch lightning model constructor.

        Example:
            model_name = 'distilbert-base-cased'
            model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=6)
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            new_word = '<NEW_LINE>'
            tokenizer.add_tokens(new_word)
            model.resize_token_embeddings(len(tokenizer))
            return model, tokenizer

        Another example:
            model = nn.Sequential(
                nn.Linear(28 * 28, 64),
                nn.ReLU(),
                nn.Linear(64, 3),
                nn.Linear(3, 64),
                nn.ReLU(),
                nn.Linear(64, 28 * 28)
            )

        """
        model = None
        tokenizer = None

        if model is None:
            raise Exception("load_model() not defined. please define in network_module.py")

        return model, tokenizer
