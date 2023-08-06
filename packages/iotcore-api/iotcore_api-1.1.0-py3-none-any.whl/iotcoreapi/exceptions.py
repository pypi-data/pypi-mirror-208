import requests


class VoidDataframeException(Exception):
    def __init__(self, message='dataframe is empty'):
        self.message = message
        # Show full traceback
        super().__init__(self.message)


class CorruptDataframeException(Exception):
    def __init__(self, df, message='dataframe does not match Nexus structure'):
        self.message = f'{message} - {df.head()}'
        self.df = df
        # Show full traceback
        super().__init__(self.message)


class IotCoreAPIException(Exception):
    """
    Nexus API exception class. Retrieves info from response object from Nexus
    """

    def __init__(self, response: requests.Response, message='NexusAPI connection error'):
        self.response = response
        self.status_code = response.status_code
        self.text = response.text
        self.message = f'{message}. Reason: {response.reason}. {self.text}'
        super().__init__(self.message)
