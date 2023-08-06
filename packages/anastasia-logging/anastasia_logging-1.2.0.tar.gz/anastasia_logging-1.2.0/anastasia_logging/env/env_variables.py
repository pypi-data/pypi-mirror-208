import os

from dataclasses import dataclass

@dataclass
class EnvironmentVariables:
    """
    Holds environment variables that AnastasiaLogger can recieve

    """

    ANASTASIA_LOG_NAME: str = os.getenv("ANASTASIA_LOG_NAME", "anastasia-log")
    ANASTASIA_LOG_TAG: str = os.getenv("ANASTASIA_LOG_TAG", "ANASTASIA-JOB")
    ANASTASIA_LOG_LEVEL: str = os.getenv("ANASTASIA_LOG_LEVEL", "INFO")
    ANASTASIA_LOG_SAVELOG: bool = os.getenv("ANASTASIA_LOG_SAVELOG", False)
    ANASTASIA_LOG_PATH: str = os.getenv("ANASTASIA_LOG_TAG", "anastasia-log.log")