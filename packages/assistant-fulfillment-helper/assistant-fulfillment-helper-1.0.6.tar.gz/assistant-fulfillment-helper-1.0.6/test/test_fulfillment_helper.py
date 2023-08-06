from mock import MagicMock
from test.mocks import constants
from assistant_fulfillment_helper.fulfillment_helper import FulfillmentHelper
from assistant_fulfillment_helper.app.responses.fulfillment_helper_response import FulfillmentHelperResponse
from assistant_fulfillment_helper.app.server.fulfillment_server import FulfillmentServer
from assistant_fulfillment_helper.app.data.webhook_data import WebhookData
from assistant_fulfillment_helper.app.models.intent_model import IntentModel

FulfillmentServer.run = MagicMock()

class TestFulfillmentHelper:

    def test_recovery_intent(self):
        node_name = 'test_recovery_intent'
        path_name = 'test_path'

        fh = FulfillmentHelper()
        @fh.intent(path_name, node=node_name, token=constants.FAKE_TOKEN)
        def callback_test(args:dict):
            return FulfillmentHelperResponse(
                message=constants.FAKE_SUCCESS_MESSAGE
            )
    
        assert WebhookData.load_intent(
            _webhook = WebhookData.get(path_name),
            intent_name=node_name,
            intent_token=constants.FAKE_TOKEN
        ) == IntentModel(
            callback = callback_test,
            webhook_token = constants.FAKE_TOKEN,
            node_name = node_name
        )

    def test_recovery_intent_deprecated(self):
        node_name = 'test_recovery_intent_deprecated'
        def callback_test(args:dict):
            return FulfillmentHelperResponse(
                message=constants.FAKE_SUCCESS_MESSAGE
            )
        
        fh = FulfillmentHelper()
        fh.registerIntent(
            callback=callback_test,
            webhook_token=constants.FAKE_TOKEN,
            node_name=node_name
        )
    
        assert WebhookData.load_intent(
            _webhook = WebhookData.get(''),
            intent_name=node_name,
            intent_token=constants.FAKE_TOKEN
        ) == IntentModel(
            callback = callback_test,
            webhook_token = constants.FAKE_TOKEN,
            node_name = node_name
        )

    def test_start_server(self):
        fh = FulfillmentHelper()
        assert fh.start(
            debug=True,
            host="123.456.789.012",
            port=1000
        ) == None # None == no errors
