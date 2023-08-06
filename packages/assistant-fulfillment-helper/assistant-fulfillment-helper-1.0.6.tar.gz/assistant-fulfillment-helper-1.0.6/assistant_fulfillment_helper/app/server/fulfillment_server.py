from . import create_app
from flask_cors import CORS

application = create_app()
CORS(application)

class FulfillmentServer:
    """ Class to handle the server context
    """

    def run(self, _host:str = '0.0.0.0', _port:int = 5052, _debug:bool = False):
        """ Start the webhook server by itself

        Args:
            _host (str) : Webhook path to get intents definition
            _port (int) : Webhook path to get intents definition
            _debug (bool) : Webhook path to get intents definition
        """
        application.run(
            host=_host, 
            port=_port, 
            debug=_debug
        )

    def get_app_context(self):
        """ Get the webhook context

        Returns:
            application (Flask) : Flask app context
        """
        return application

