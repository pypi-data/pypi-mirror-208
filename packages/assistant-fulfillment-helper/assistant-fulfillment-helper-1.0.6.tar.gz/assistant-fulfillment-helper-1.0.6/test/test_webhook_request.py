import json
import pytest
from test.mocks import constants
from assistant_fulfillment_helper.fulfillment_helper import FulfillmentHelper
from assistant_fulfillment_helper.app.responses.fulfillment_helper_response import FulfillmentHelperResponse

fh = FulfillmentHelper()
class TestWebhookRequest:

    def test_health_check_success(self, client):
        response = client.get('/')
        assert response.json == dict(
            message = "This is a TOTVS Assistant Webhook Server. See https://pypi.org/project/assistant-fulfillment-helper/ for more details"
        )

    def test_webhook_request_unauthenticated_default_path(self, client):
        response = client.post('/')
        assert response.status_code == 401
        assert response.json == dict(
            message = 'Authorization, or X-Auth-Key and X-Auth-ConnectorId is invalid. Please authenticate.'
        )

    def test_webhook_request_unauthenticated_webhook_path(self, client):
        webhook_path = 'test_webhook_request_unauthenticated_webhook_path'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)

        response = client.post(f'/{webhook_path}')
        assert response.status_code == 401
        assert response.json == dict(
            message = 'Authorization, or X-Auth-Key and X-Auth-ConnectorId is invalid. Please authenticate.'
        )

    def test_webhook_response(self, client):
        webhook_path = 'test_webhook_response'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json == dict(
            jump_to = None,
            logout = False,
            message = constants.FAKE_SUCCESS_MESSAGE,
            options = None,
            parameters = None,
            short_message = None
        )

    def test_webhook_response_deprecated_intent(self, client):
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        fh.registerIntent(callback_test, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        
        response = client.post('/',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json == dict(
            jump_to = None,
            logout = False,
            message = constants.FAKE_SUCCESS_MESSAGE,
            options = None,
            parameters = None,
            short_message = None
        )

    def test_webhook_request_wrong_token(self, client):
        webhook_path = 'test_webhook_request_wrong_token'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : f'trunc_{constants.FAKE_TOKEN}'},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 401
        assert response.json == dict(
            message = 'Authorization, or X-Auth-Key and X-Auth-ConnectorId is invalid. Please authenticate.'
        )

    def test_webhook_request_wrong_auth_header(self, client):
        webhook_path = 'test_webhook_request_wrong_token'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, f"constants.FAKE_PARAMS.get('intent_name')")
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        response = client.post(f'/{webhook_path}',
            headers={'Authorization' : f'{constants.FAKE_TOKEN}'},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 401
        assert response.json == dict(
            message = 'Authorization, or X-Auth-Key and X-Auth-ConnectorId is invalid. Please authenticate.'
        )

    def test_webhook_request_wrong_intent(self, client):
        webhook_path = 'test_webhook_request_wrong_intent'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        params = constants.FAKE_PARAMS
        params['intent_name'] = 'truncated intent'
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(params),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert response.json == dict(
            error = f"Nenhum callback foi encontrado para a intenção '{params['intent_name']}'"
        )

    def test_webhook_request_undefined_path(self, client):
        webhook_path = 'test_webhook_request_wrong_intent'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(message=constants.FAKE_SUCCESS_MESSAGE)
        
        undefined_path = 'undefined_path'
        response = client.post(f'/{undefined_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert response.json == dict(
            error = f"O path '{undefined_path}' não foi definido para nenhum webhook."
        )

    def test_webhook_request_wrong_callback_response(self, client):
        webhook_path = 'test_webhook_request_wrong_callback_response'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return dict(message=constants.FAKE_SUCCESS_MESSAGE)
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert response.json == dict(
            error = f"O callback 'callback_test' deve retornar uma classe do tipo 'FulfillmentHelperResponse'"
        )

    def test_webhook_request_wrong_callback_processing(self, client):
        webhook_path = 'test_webhook_request_wrong_callback_processing'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            trunc_condition = 'a'/0*dict()
            return FulfillmentHelperResponse(message=trunc_condition)
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json == dict(
            message = "Desculpe, não consegui processar seu pedido no momento."
        )

    def test_webhook_request_wrong_callback_processing_with_fallback(self, client):
        webhook_path = 'test_webhook_request_wrong_callback_processing_with_fallback'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'), 
            fallback_message=constants.FAKE_FALLBACK_MESSAGE
        )
        def callback_test(args:dict):
            trunc_condition = 'a'/0*dict()
            return FulfillmentHelperResponse(message=trunc_condition)
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json == dict(
            message = constants.FAKE_FALLBACK_MESSAGE
        )

    def test_webhook_request_params(self, client):
        webhook_path = 'test_webhook_request_params'
        @fh.intent(webhook_path, constants.FAKE_TOKEN, constants.FAKE_PARAMS.get('intent_name'))
        def callback_test(args:dict):
            return FulfillmentHelperResponse(
                message=constants.FAKE_SUCCESS_MESSAGE,
                short_message = constants.FAKE_SHORT_MESSAGE,
                jump_to = constants.FAKE_JUMP_TO,
                options = constants.FAKE_OPTIONS,
                logout = constants.FAKE_LOGOUT_TRUE,
                parameters = constants.FAKE_PARAMETERS
            )
        
        response = client.post(f'/{webhook_path}',
            headers={'X-Assistant-Signature-Token' : constants.FAKE_TOKEN},
            data=json.dumps(constants.FAKE_PARAMS),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json == dict(
            jump_to = constants.FAKE_JUMP_TO,
            logout =  constants.FAKE_LOGOUT_TRUE,
            message = constants.FAKE_SUCCESS_MESSAGE,
            options = constants.FAKE_OPTIONS,
            parameters = constants.FAKE_PARAMETERS,
            short_message = constants.FAKE_SHORT_MESSAGE,
        )
