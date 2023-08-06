class AnalyticsLibError(Exception):
    pass


class InvalidArnException(AnalyticsLibError):
    pass


class LivyConnectionError(AnalyticsLibError):
    pass


class MissingParametersError(AnalyticsLibError):
    pass


class InvalidParameterError(AnalyticsLibError):
    pass


class InvalidConfigError(AnalyticsLibError):
    pass
