import traceback


class APIError(Exception):
    """All custom API Exceptions"""

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code

        self.payload = payload
        self.traceback = traceback.format_exc()