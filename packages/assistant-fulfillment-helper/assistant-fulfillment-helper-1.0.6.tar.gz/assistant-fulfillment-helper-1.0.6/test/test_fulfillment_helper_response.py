import pytest
from assistant_fulfillment_helper.app.responses.fulfillment_helper_response import FulfillmentHelperResponse

class TestFulfillmentHelperResponse:

    def test_create_response_without_message_param(self):
        with pytest.raises(TypeError) as e_info:
            FulfillmentHelperResponse(
                jump_to = 'jump_to'
            )
        assert "required positional argument: 'message'" in e_info.value.args[0]

    def test_create_response_with_non_expected_params(self):
        with pytest.raises(TypeError) as e_info:
            FulfillmentHelperResponse(
                message = 'message',
                foreign_param = 'foreign_param'
            )
        assert "unexpected keyword argument 'foreign_param'" in e_info.value.args[0]
        
    def test_create_full_response_success(self):
        response = FulfillmentHelperResponse(
            message = 'message',
            short_message = 'short_message',
            jump_to = 'jump_to',
            options = ["opt1", "opt2"],
            logout = True,
            parameters = {'test_param': 'test_value'}
        )
        assert response.message == 'message'
        assert response.short_message == 'short_message'
        assert response.jump_to == 'jump_to'
        assert response.options == ["opt1", "opt2"]
        assert response.logout == True
        assert response.parameters == {'test_param': 'test_value'}

     