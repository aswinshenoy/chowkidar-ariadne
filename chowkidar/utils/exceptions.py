
class AuthError(ValueError):
    def __init__(self, message, code=None):
        if code:
            self.code = code
        super().__init__(message)
