from typing import Any


class ZIDSNetwork:
    """! Base class for neural network definition:

    Example:
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

    for example:
        @code
            model = nn.Sequential(
                nn.Linear(28 * 28, 64),
                nn.ReLU(),
                nn.Linear(64, 3),
            )
        @endcode

    Another example:
        @code
        self.bert = BertModel.from_pretrained("bert-base-cased")
        @endcode
    """

    model = None

    def __init__(self, model=None):

        self.model = model

    @staticmethod
    def load_define_model():
        """ Load/Define model here, getting called from plmodel.py


        Example:
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
                model = nn.Sequential(
                    nn.Linear(28 * 28, 64),
                    nn.ReLU(),
                    nn.Linear(64, 3),
                )
            @endcode

        Another example:
            @code
                self.bert = BertModel.from_pretrained("bert-base-cased")
            @endcode

        Returns:

        """
        model = None
        tokenizer = None

        if model is None:
            raise Exception("load_model() not defined. please define in network_module.py")

        return model, tokenizer
