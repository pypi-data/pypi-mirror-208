from logging import basicConfig
from logging import getLogger
from logging import INFO
from logging import WARNING
from logging import ERROR
from logging import CRITICAL
from logging import DEBUG
from os import getenv
import logging
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


class Log:
    '''
    'debug'
    'info'
    'warning'
    'error'
    'critical'

    remeber me -- principle context propagation say

    '''

    def __init__(
        self,
        path_file: str = None,
        level: int = None,
        is_local_env: bool = False,
        event_level = None
    ) -> None:

        self.is_local_env = is_local_env
        self.filename = path_file
        self.LOGFORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        self.DEFAULT_LEVEL = (
            'info'  # Your default level, usually set to warning or error for production
        )

        self.level = level
        self.event_level = event_level

        self.LEVELS = {
            'debug': DEBUG,
            'info': INFO,
            'warning': WARNING,
            'error': ERROR,
            'critical': CRITICAL,
        }

    # Iniciar logs
    def startlogging(self):

        basicConfig(
            level=self.LEVELS[self.level],
            format=self.LOGFORMAT,
            force=True,
            handlers=[
                logging.FileHandler(self.filename),
                logging.StreamHandler(sys.stdout)
            ]
        )

        if self.is_local_env is not True:
            # All of this is already happening by default!
            sentry_logging = LoggingIntegration(
                # Capture info and above as breadcrumbs
                level = self.LEVELS[self.level],
                # Send errors as events
                event_level = self.LEVELS[self.event_level],
            )
            sentry_sdk.init(
                dsn=getenv('SENTRY_DSN'),
                environment = getenv("NODE_ENV"),
                integrations=[
                    sentry_logging,
                ],
                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                # We recommend adjusting this value in production,
                traces_sample_rate=1.0,
            )

    def get_log(self, message):
        return getLogger(message)
