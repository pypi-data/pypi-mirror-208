import logging
from flask import Blueprint
from assistant_fulfillment_helper.app.controllers.webhook_controller import WebhookController
from assistant_fulfillment_helper.app.controllers.auth_controller import AuthController

server_bp = Blueprint('main', __name__)
auth = AuthController()


@server_bp.route('/', methods=['GET'])
def index():
    """ Health check route

    .. versionadded:: 0.0.1
    """
    return {
        'message': 'This is a TOTVS Assistant Webhook Server. See https://pypi.org/project/assistant-fulfillment-helper/ for more details'
    }, 200


@server_bp.route('/', methods=['POST'])
@auth.validate_auth
def default():
    """ Default route to handle deprecated Assistant request
    
    .. versionadded:: 0.0.1
    """
    return WebhookController('').process_request()


@server_bp.route('/<webhook>', methods=['POST'])
@auth.validate_auth
def main(webhook):
    """ Default route to handle Assistant request
    
    .. versionadded:: 1.0.5
    """
    return WebhookController(webhook).process_request()