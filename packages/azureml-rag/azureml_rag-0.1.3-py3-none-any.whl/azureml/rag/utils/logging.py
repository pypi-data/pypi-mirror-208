# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging utilities."""
import logging
import sys


# class ExtraPrintHandler(logging.StreamHandler):
#     LEVELS = {0: 'DBUG', 1: 'INFO', 2: 'WARN', 3: 'ERRR'}

#     def emit(self, record):
#         if hasattr(record, 'print') and record.print:
#             print(f'[{datetime.utcnow()}] {record.levelname} - {record.msg}')
#         super().emit(record)

# handler = ExtraPrintHandler()


class LoggerFactory:
    """Factory for creating loggers"""
    def __init__(self, stdout=False):
        """Initialize the logger factory"""
        self.loggers = {}
        self.stdout = stdout

    def with_stdout(self, stdout=True):
        """Set whether to log to stdout"""
        self.stdout = stdout
        # Add stdout handler to any loggers created before enabling stdout.
        for logger in self.loggers.values():
            if self.stdout:
                stdout_handler = logging.StreamHandler(stream=sys.stdout)
                stdout_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)s - %(message)s (%(filename)s:%(lineno)s)', "%Y-%m-%d %H:%M:%S"))
                logger.addHandler(stdout_handler)
        return self

    def get_logger(self, name, level=logging.INFO):
        """Get a logger with the given name and level"""
        if name not in self.loggers:
            logger = logging.getLogger(f'azureml.rag.{name}')
            logger.setLevel(level)
            if self.stdout:
                stdout_handler = logging.StreamHandler(stream=sys.stdout)
                stdout_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)s - %(message)s (%(filename)s:%(lineno)s)', "%Y-%m-%d %H:%M:%S"))
                logger.addHandler(stdout_handler)
            self.loggers[name] = logger
        return self.loggers[name]


_logger_factory = LoggerFactory()


def enable_stdout_logging():
    """Enable logging to stdout"""
    _logger_factory.with_stdout(True)


def get_logger(name, level=logging.INFO):
    """Get a logger with the given name and level"""
    return _logger_factory.get_logger(name, level)
