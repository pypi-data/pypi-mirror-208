# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file contains telemetry PII stripping formatter."""

from logging import LogRecord

from azureml.automl.core.shared.exceptions import NON_PII_MESSAGE
from azureml.automl.core.shared.telemetry_formatter import AppInsightsPIIStrippingFormatter


class AppInsightsPIIStrippingAllMessagesFormatter(AppInsightsPIIStrippingFormatter):
    """Formatter that will prevent any PII debug/info/warning/exception from getting logged"""

    # Following is the allow-list of messages to log in app-insight if they are generating outside the azureml
    # packages.
    # Dev Notes: Add only PII-free messages to whitelist from non azureml packages.
    ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS = []

    def format(self, record: LogRecord) -> str:
        """
        Modify the log record to strip log messages if they originate from a non-AzureML packages and not matches
        the ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS

        :param record: Logging record.
        :return: Formatted record message.
        """
        message = record.getMessage()

        if record.name.startswith("azureml.") or any(allowed_patern in message for allowed_patern in
                                                     self.ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS):
            return super().format(record)
        else:
            record.message = NON_PII_MESSAGE
            record.msg = NON_PII_MESSAGE
            return super().format(record)
