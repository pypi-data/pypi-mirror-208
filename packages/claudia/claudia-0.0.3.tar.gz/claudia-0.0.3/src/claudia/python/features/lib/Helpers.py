import os

from features.exceptions.UnconfiguredEnvironmentException import UnconfiguredEnvironmentException


def read_env_var(key):
    if not os.environ.get(key, None):
        raise UnconfiguredEnvironmentException("'{}' is not set correctly".format(key))
    else:
        return os.environ[key]
