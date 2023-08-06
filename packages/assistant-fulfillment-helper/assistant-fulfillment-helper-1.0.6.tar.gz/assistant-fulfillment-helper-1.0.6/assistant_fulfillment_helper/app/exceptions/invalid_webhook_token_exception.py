class InvalidWebhookTokenException(Exception):
    """Exception raised when a Intent callback was found, but with an invalid Webhook token.

    Attributes:
        intent_node -- node name that have a invalid Webhook token.
    """

    def __init__(self, intent_node):
        message = f"Token inválido para o Webhook da intenção '{intent_node}'"
        self.message = message
        super().__init__(self.message)

    