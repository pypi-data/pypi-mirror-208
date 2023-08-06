class DuplicatedIntentNodeException(Exception):
    """Exception raised for register intent with duplicated node_name.

    Attributes:
        intent_node -- node name that is duplicated
    """

    def __init__(self, intent_node):
        message = f"A intenção '{intent_node}' já foi declarada anteriormente."
        self.message = message
        super().__init__(self.message)

    