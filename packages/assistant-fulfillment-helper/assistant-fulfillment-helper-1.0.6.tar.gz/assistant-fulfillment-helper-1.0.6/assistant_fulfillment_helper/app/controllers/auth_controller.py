from flask import request, jsonify
from functools import wraps
from assistant_fulfillment_helper.app.data.token_data import TokenData


class AuthController:
    """Controller class to handler authentication
    """

    def validate_auth(self, f):
        """ @decorator_method
        Validates if a valid token exists in request header 

        .. versionadded:: 1.0.5
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            headers = request.headers
            if headers and TokenData.validate(headers.get('X-Assistant-Signature-Token')):
                return f(*args, **kwargs)
            return self.__forbidden_auth()
        return decorated
    

    def __forbidden_auth(self):
        """ Handle forbidded requests

        .. versionadded:: 1.0.5

        Returns:
            resp (dict): default forbidden json for missing or wrong token
        """
        message = 'Authorization, or X-Auth-Key and X-Auth-ConnectorId is invalid. Please authenticate.'
        resp = jsonify({"message": message})
        resp.status_code = 401
        return resp
