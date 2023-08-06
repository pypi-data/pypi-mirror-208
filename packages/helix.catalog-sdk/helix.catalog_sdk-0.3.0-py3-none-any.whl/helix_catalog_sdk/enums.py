from enum import Enum


class HelixEnvironment(Enum):
    PRODUCTION = 1
    PROD = 1
    STAGING = 2
    QA = 3
    DEV = 4
    CLIENT_SANDBOX = 5
