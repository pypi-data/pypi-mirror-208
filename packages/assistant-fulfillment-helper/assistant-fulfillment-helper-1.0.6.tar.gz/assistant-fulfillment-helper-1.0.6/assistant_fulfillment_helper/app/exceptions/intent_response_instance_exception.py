class IntentResponseInstanceException(Exception):
    """Exception raised for wrong response from an intent.

    Attributes:
        callback_name -- callback that have a wrong response
    """

    def __init__(self, callback_name):
        message = f"O callback '{callback_name}' deve retornar uma classe do tipo 'FulfillmentHelperResponse'"
        self.message = message
        super().__init__(self.message)

    