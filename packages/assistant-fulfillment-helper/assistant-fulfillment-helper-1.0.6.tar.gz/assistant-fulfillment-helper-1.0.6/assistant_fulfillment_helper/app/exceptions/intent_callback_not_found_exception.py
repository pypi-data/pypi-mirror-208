class IntentCallbackNotFoundException(Exception):
    """Exception raised when a node_name wasn't found in Intents list. 
    That means it wasn't defined previously.

    Attributes:
        intent_node -- node name that was not found
    """

    def __init__(self, intent_node):
        message = f"Nenhum callback foi encontrado para a intenção '{intent_node}'"
        self.message = message
        super().__init__(self.message)

    