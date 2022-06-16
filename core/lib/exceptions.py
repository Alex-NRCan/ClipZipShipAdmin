"""
This module offers application exceptions.
"""


class ApplicationException(Exception):
    """Base class for Exceptions for the Application"""
    pass


class UserMessageException(ApplicationException):
    """Exception raised when a message (likely an error message) needs to be sent to the User."""
    def __init__(self, code, message, message_fr):
        super(UserMessageException, self)
        self.code = code
        self.title = "Error"
        if code == 500:
            self.title = "Internal Server Error"
        elif code == 400:
            self.title = "Bad Request"
        elif code == 401:
            self.title = "Unauthorized"
        elif code == 403:
            self.title = "Forbidden"
        elif code == 404:
            self.title = "Not Found"
        elif code == 405:
            self.title = "Method Not Allowed"
        elif code == 429:
            self.title = "Too Many Requests"
        self.message = message
        self.message_fr = message_fr

    def __str__(self):
        return "ENG: " + self.message + " | FR: " + self.message_fr


class ParametersInvalidException(UserMessageException):
    """Exception raised when parameters used in a query are invalid."""
    def __init__(self):
        super(ParametersInvalidException, self).__init__(400, "Invalid parameters", "Paramètres invalides")


class TokenMissingException(UserMessageException):
    """Exception raised when parameters used in a query are invalid."""
    def __init__(self):
        super(TokenMissingException, self).__init__(401, "Token is missing", "Le jeton est manquant")


class TokenInvalidException(UserMessageException):
    """Exception raised when an invalid token is being used in a query."""
    def __init__(self):
        super(TokenInvalidException, self).__init__(401, "Token is invalid", "Le jeton est invalide")


class TokenExpiredException(UserMessageException):
    """Exception raised when an expired token is being used in a query."""
    def __init__(self):
        super(TokenExpiredException, self).__init__(401, "Token has expired", "Le jeton est expiré")


class TokenRevokedException(UserMessageException):
    """Exception raised when a deleted token is being used in a query."""
    def __init__(self):
        super(TokenRevokedException, self).__init__(401, "Token has been revoked", "Le jeton a été supprimé")


class TokenInsufficientException(UserMessageException):
    """Exception raised when the user doesn't have enough privileges to execute the query."""
    def __init__(self):
        super(TokenInsufficientException, self).__init__(403, "Insufficient privileges", "Privilèges insuffisants")


class NotFoundException(UserMessageException):
    """Exception raised when an endpoint couldn't be found."""
    def __init__(self):
        super(NotFoundException, self).__init__(404, "URL or information not found", "URL ou information introuvable")


class MethodNotAllowedException(UserMessageException):
    """Exception raised when a user calls an endpoint using the wrong HTTP VERB."""
    def __init__(self):
        super(MethodNotAllowedException, self).__init__(405, "The method is not allowed for the requested URL",
                                                        "Méthode d'appel défendu pour l'URL demandé")


class RateLimitedException(UserMessageException):
    """Exception raised when a user is being rate-limited."""
    def __init__(self, reason):
        super(RateLimitedException, self).__init__(429,
                                                   "You've sent too many requests. Do not go over " + reason + ".",
                                                   "Vous avez effectué trop de requêtes. Ne dépassez pas " + reason.replace(
                                                       "per", "par") + ".")
