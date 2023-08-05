class ZoomOAuthClient:
    """
    A class representing a Zoom OAuth Client.

    :param account_id: The account ID for the app.
    :param client_id: The client ID for the app.
    :param client_secret: The client secret for the app.
    """
    def __init__(self, account_id: str, client_id: str, client_secret: str) -> None: ...

    def get_access_token(self) -> str:
        """
        Gets a new access token from the Zoom OAuth API.

        Returns:
            The new access token as a string.
        """

    def __repr__(self) -> str:
        """
        Gets a string representation of the `ZoomOAuthClient` instance.

        Returns:
            The string representation of the instance.
        """
