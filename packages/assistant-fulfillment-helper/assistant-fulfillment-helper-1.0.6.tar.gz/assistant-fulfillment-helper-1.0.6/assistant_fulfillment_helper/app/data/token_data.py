
class TokenData:
    """ DataClass to handle all nodes tokens. Used to match authentication on AuthController()
    """

    __tokens = []

    @staticmethod
    def validate(token: str) -> bool:
        """ Search a token on defined token list previously

        Args:
            token (str) : Token receipt from webhook request header

        Returns:
            (bool) : Indicates whether the token is known for the webhook
        """
        if token in TokenData.__tokens:
            return True
        return False
    
    @staticmethod
    def set_token(token: str):
        """ Define a token to the know tokens list

        Args:
            token (str) : Token to input on the know tokens list
        """
        if token not in TokenData.__tokens:
            TokenData.__tokens.append(token)
