import logging
from flask import request
from webargs import fields
from webargs.flaskparser import parser
from assistant_fulfillment_helper.app.data.webhook_data import WebhookData
from assistant_fulfillment_helper.app.responses.fulfillment_helper_response import FulfillmentHelperResponse
from assistant_fulfillment_helper.app.exceptions import IntentResponseInstanceException
from assistant_fulfillment_helper.app.exceptions import InvalidWebhookTokenException
from assistant_fulfillment_helper.app.exceptions import IntentCallbackNotFoundException
from assistant_fulfillment_helper.app.exceptions import WebhookNotFoundException


logger = logging.getLogger(__name__)

class WebhookController:
    """ Class to handle all webhook requests
    """

    def __init__(self, webhook) -> None:
        """ Defines wich webhook the request is coming from
        """
        self.__webhook = webhook
        
    def process_request(self):
        """ Process the receipt request

        .. versionadded:: 1.0.5

        Returns:
            (dict): structured dict attending Assistant contract to send a message response
        """
        args = self.__parse_args()

        try:
            intent = WebhookData.load_intent(
                WebhookData.get(self.__webhook),
                args.get('intent_name'),
                request.headers.get("X-Assistant-Signature-Token")
            )

            results = intent.callback(args)
            if isinstance(results, FulfillmentHelperResponse) == False:
                raise IntentResponseInstanceException(intent.callback.__name__)
            
            return dict(
                message = results.message,
                short_message = results.short_message,
                jump_to = results.jump_to,
                options = results.options,
                logout = results.logout,
                parameters = results.parameters
            )
        except (
            IntentResponseInstanceException,
            InvalidWebhookTokenException,
            IntentCallbackNotFoundException,
            WebhookNotFoundException
        ) as e:
            return self.__error_handler(e)
        except Exception as e:
            logger.error(f"Error while calling a callback: {e}.")
        
        if intent and intent.fallback_message:
            fallback_message = intent.fallback_message
        else:    
            fallback_message = "Desculpe, não consegui processar seu pedido no momento."

        return dict(
            message = fallback_message
        )

    def __parse_args(self):
        """ Parse mandatory args attending Assistant contract

        .. versionadded:: 0.0.1

        Returns:
            (dict): a dict with all parsed madatory request args
        """
        # Try to parse threshold as a dict on the first attempt
        query_arg = {
            "intent_name":              fields.Str(required=True,   description='The node being processed.'),
            "parameters":               fields.Dict(required=True,  description='All the context parameters.'),
            "sessionLog":               fields.List(fields.Dict(),  required=True, description='Logs up to the current point.'),
            "namedQueries":             fields.Dict(required=False, missing={}, description='named query results, if any.'),
            "query":                    fields.Str(required=True,   description='The node being processed.'),
            "message":                  fields.Str(required=True,   description='The node being processed.'),
            "language":                 fields.Str(required=False,  missing="", description='The node being processed.'),
            "allRequiredParamsPresent": fields.Bool(required=False, missing=True),
            "carolOrganization":        fields.Str(required=True,   description='Carol organization name.'),
            "carolEnvironment":         fields.Str(required=True,   description='Carol tenant name.'),
            "carolOrganizationId":      fields.Str(required=True,   description='Carol organization id.'),
            "carolEnvironmentId":       fields.Str(required=True,   description='Carol tenant id.'),
            "sessionId":                fields.Str(required=True,   description='The current conversation session.'),
            "isProduction":             fields.Bool(required=False, missing=False),
            "channelName":              fields.Str(required=True,   description='The channel which the message is comming from.')
        }

        return parser.parse(query_arg, request)
    

    def __error_handler(self, error):
        logger.error(f"ERROR: [webhook request] {error.args[0]}")
        return dict(error=error.args[0]), 400