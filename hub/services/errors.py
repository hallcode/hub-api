from flask import current_app


class Error(Exception):
    """Base exception for application level errors."""
    
    def __init__(self, message="There was a problem.", code=500):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'[{self.code}] {self.message}'


class ActionNotAllowed(Error):
    """Standard authentication error (i.e. user does not have required access to perform action)."""
    def __init__(self):
        self.code = 403
        self.message = "You are not allowed to perform that action"
        super().__init__(self.message, self.code)


class UserNotAuthenticated(Error):
    """Error for when the user is not logged in."""
    def __init__(self):
        self.code = 401
        self.message = "You must be logged in to perform this action"
        super().__init__(self.message, self.code)


class TokenError(Error):
    """Base error for token authentication issues."""
    def __init__(self):
        self.code = 401
        self.message = "Authentication token not valid"
        super().__init__(self.message, self.code)


class NotFoundError(Error):
    """Generate a HTTP 404 error."""
    def __init__(self, resource):
        self.resource_name = resource.__tablename__
        self.code = 404
        self.message = f"{self.resource_name.title()} not found"
        super().__init__(self.message, self.code)