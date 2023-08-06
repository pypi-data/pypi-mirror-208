class FulfillmentHelperContext:
    
    def __init__(self) -> None:
        self.__context_intents = []
    
    def intent(self, webhook:str, token:str, node:str, fallback_message:str = None) -> any:
        """ @decorator_method
        Defines a callback method for webhook requests from Assistant in a independent context.

        .. versionadded:: 1.0.6

        Args:
            webhook (str): The path for webhook server that will receive requests
            token (str): The webhook token provided by Assistant UI
            node (str): The name of node created on Asisstant
            fallback_message (str): Fallback client message in case of callback error
        """
        def wrapper_intent(f):
            self.__context_intents.append(dict(
                callback=f,
                webhook_token=token,
                node_name=node,
                webhook_path=webhook,
                fallback_message=fallback_message
            ))
            return f
        return wrapper_intent
    

    def registerIntent(self, callback:callable, webhook_token:str, node_name:str) -> None:
        """ DEPRECATED METHOD
        Defines a callback method for webhook requests from Assistant in an indepentend context. 

        .. versionadded:: 0.0.1

        Args:
            callback (callable): Method to be called for requests in this intent 
            webhook_token (str): The webhook token provided by Assistant UI
            node_name (str): The name of node created on Asisstant
        """
        self.__context_intents.append(dict(
            callback=callback,
            webhook_token=webhook_token,
            node_name=node_name
        ))
        
    
    def get_intents(self):
        """ 
        Return context intents list

        .. versionadded:: 1.0.6
        """
        return self.__context_intents