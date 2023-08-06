from assistant_fulfillment_helper.app.exceptions import *
from assistant_fulfillment_helper.app.models.intent_model import IntentModel

class WebhookData:
    """ DataClass to handle webhooks definitions.
    """

    __webhooks = {}

    @staticmethod
    def get(webhook):
        """ Search a webhook definition on the storage list

        Args:
            webhook (str) : Webhook path to get intents definition

        Returns:
            list(IntentModel) : List of intentions declared to the webhook

        Raises:
            WebhookNotFoundException: when the webhook is not found in the known webhook list
        """
        if webhook == None:
            webhook = ""
            
        if webhook in WebhookData.__webhooks:
            return WebhookData.__webhooks.get(webhook)
        raise WebhookNotFoundException(webhook)
    
    @staticmethod
    def set_intent(webhook: str, intent: IntentModel):
        """ Set an intent definition ti a webhook

        Args:
            webhook (str) : Webhook path to receive the intent
            intent (IntentModel) : Intent to be added on the webhook context
        """
        if webhook == None:
            webhook = ""
            
        if webhook not in WebhookData.__webhooks:
            WebhookData.__webhooks[webhook] = []
        WebhookData.__validate_webhook_intent(webhook, intent)
        WebhookData.__webhooks[webhook].append(intent)

    @staticmethod
    def load_intent(_webhook, intent_name, intent_token):
        """ Load an intent definition from a webhook context

        Args:
            _webhook (list(MultipleDict)) : Multiple dict of intentions in a Webhook
            intent_name (str) : Name of the intent to be loaded
            intent_token (str) : Token of the intent

        Returns:
            IntentModel : Intent definitions

        Raises:
            InvalidWebhookTokenException: when the token is not the same defined for the intent
            IntentCallbackNotFoundException: when the intent is not found in the webhook context
        """
        for intent in _webhook:
            if intent.node_name == intent_name:
                if intent.webhook_token == intent_token:
                    return intent
                raise InvalidWebhookTokenException(intent_name)
        raise IntentCallbackNotFoundException(intent_name)

    @staticmethod
    def __validate_webhook_intent(webhook: str, incoming_intent: IntentModel):
        """ Validates if the incoming intent is correct to be inputed in a webhook context

        Args:
            webhook (str) : Webhook wich will receive the intent
            incoming_intent (IntentModel) : Intent definitions that will be inputed on the webhook context

        Raises:
            DuplicatedIntentNodeException: when the incoming intent is already declared on the webhook context
        """
        for w_intent in WebhookData.__webhooks[webhook]:
            if w_intent.node_name == incoming_intent.node_name:
                raise DuplicatedIntentNodeException(incoming_intent.node_name)
