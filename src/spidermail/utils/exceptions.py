"""
Custom exceptions for SpiderMail
"""


class SpiderMailException(Exception):
    """Base exception for SpiderMail"""
    pass


class DatabaseException(SpiderMailException):
    """Database related exceptions"""
    pass


class SpiderException(SpiderMailException):
    """Spider related exceptions"""
    pass


class ConfigurationError(SpiderMailException):
    """Configuration related exceptions"""
    pass


class DataValidationError(SpiderMailException):
    """Data validation exceptions"""
    pass


class NetworkException(SpiderMailException):
    """Network related exceptions"""
    pass


class RateLimitException(NetworkException):
    """Rate limiting exceptions"""
    pass


class AuthenticationException(NetworkException):
    """Authentication related exceptions"""
    pass


class ProxyException(NetworkException):
    """Proxy related exceptions"""
    pass