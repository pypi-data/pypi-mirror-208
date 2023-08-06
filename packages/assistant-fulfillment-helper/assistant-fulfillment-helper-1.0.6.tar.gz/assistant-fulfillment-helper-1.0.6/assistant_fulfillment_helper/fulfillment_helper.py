from .app.server.fulfillment_server import FulfillmentServer
from .app.models.intent_model import IntentModel
from .app.data.webhook_data import WebhookData
from .app.data.token_data import TokenData
from .fulfillment_helper_context import FulfillmentHelperContext

class FulfillmentHelper(FulfillmentServer):
    """Interface class to instance the module
    """

    def intent(self, webhook:str, token:str, node:str, fallback_message:str = None) -> any:
        """ @decorator_method
        Defines a callback method for webhook requests from Assistant.

        .. versionadded:: 1.0.5

        .. code-block:: python
            @fh.register_intent("my_webhook", token='123456' node='My node')
            def my_callback(args: dict):
                return FulfillmentHelperResponse(
                    message="Hello, It's your webhook response"
                )

        Args:
            webhook (str): The path for webhook server that will receive requests
            token (str): The webhook token provided by Assistant UI
            node (str): The name of node created on Asisstant
            fallback_message (str): Fallback client message in case of callback error
        """
        def wrapper_intent(f):
            self.__register(
                callback=f,
                webhook_token=token,
                node_name=node,
                webhook_path=webhook,
                fallback_message=fallback_message
            )
            return f
        return wrapper_intent
    

    def registerIntent(self, callback:callable, webhook_token:str, node_name:str) -> None:
        """ DEPRECATED METHOD
        Defines a callback method for webhook requests from Assistant.

        .. versionadded:: 0.0.1

        Args:
            callback (callable): Method to be called for requests in this intent 
            webhook_token (str): The webhook token provided by Assistant UI
            node_name (str): The name of node created on Asisstant
        """
        self.__register(
            callback=callback,
            webhook_token=webhook_token,
            node_name=node_name
        )
        
    def registerContext(self, Context: FulfillmentHelperContext):
        for intent in Context.get_intents():
            self.__register(
                callback=intent.get('callback'),
                webhook_token=intent.get('webhook_token'),
                node_name=intent.get('node_name'),
                webhook_path=intent.get('webhook_path'),
                fallback_message=intent.get('fallback_message')
            )

    def __register(self, callback:callable, webhook_token:str, node_name:str, webhook_path:str = '', fallback_message:str = None) -> None:
        """ Privated method to storage the intents and webhooks from intent() and registerIntent()

        .. versionadded:: 1.0.5

        Args:
            callback (callable): Method to be called for requests in this intent 
            webhook (str): The path for webhook server that will receive requests
            node_name (str): The name of node created on Asisstant
            webhook_token (str): The webhook token provided by Assistant UI
        """
        webhook_path = '' if webhook_path == None else webhook_path
        
        intent = IntentModel(
            callback = callback,
            webhook_token = webhook_token,
            node_name = node_name,
            fallback_message = fallback_message
        )
        WebhookData.set_intent(webhook=webhook_path, intent=intent)
        TokenData.set_token(token=webhook_token)


    def start(self, host='0.0.0.0', port=5052, debug=False) -> None:
        """Runs the Webhook server

        .. versionadded:: 0.0.1

        Args:
            host (str): Host defined to the application
            port (int): Port defined to the application
            debug (bool): Run the webhook in debug mode
        """
        self.run(host, port, debug)
