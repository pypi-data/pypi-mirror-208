class ErrorCodes:
    INVALID_ATTRIBUTE = 'Invalid attribute!'
    ENVIRONMENT_ERROR = 'Invalid environment!'
    ACCESS_TOKEN_ERROR = 'Invalid access token!'
    BASE_URL_ERROR = 'Invalid base url!'


class TremendousException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
