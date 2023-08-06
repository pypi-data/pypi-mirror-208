class WebhookNotFoundException(Exception):
    """Exception raised when a undeclared webhook is called.

    Attributes:
        webhook_path -- path from request is coming
    """

    def __init__(self, webhook_path):
        message = f"O path '{webhook_path}' não foi definido para nenhum webhook."
        self.message = message
        super().__init__(self.message)

    