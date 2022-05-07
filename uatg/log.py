# See LICENSE.incore for details

from logging import ERROR, CRITICAL, WARNING, INFO, DEBUG, getLogger, \
    StreamHandler, root
from colorlog import ColoredFormatter
from sys import stdout


class Log:
    """
    this class holds all the logic; see the end of the script to
    see how it's instantiated in order to have the line
    "from zenlog import log" work
    """

    aliases = {
        CRITICAL: ("critical", "crit", "fatal"),
        ERROR: ("error", "err"),
        WARNING: ("warning", "warn"),
        INFO: ("info", "inf"),
        DEBUG: ("debug", "dbg")
    }

    def __init__(self, _format=None):
        self.stream = None
        self._lvl = None
        if not _format:
            _format = "%(log_color)s%(levelname)8s%(reset)s | %(log_color)" \
                     "s%(message)s%(reset)s"
        self.format = _format
        self.colors = {
            'DEBUG': 'purple',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red',
        }
        self.logger = getLogger("uatg")

    # the magic happens here: we use the "extra" argument documented in
    # https://docs.python.org/2/library/logging.html#logging.Logger.debug
    # to inject new items into the logging.LogRecord objects
    # we also create our convenience methods here
    def critical(self, message, *args, **kwargs):
        for line in str(message).splitlines():
            self.logger.critical(line, *args, **kwargs)

    crit = c = fatal = critical

    def error(self, message, *args, **kwargs):
        for line in str(message).splitlines():
            self.logger.error(line, *args, **kwargs)

    err = e = error

    def warn(self, message, *args, **kwargs):
        for line in str(message).splitlines():
            self.logger.warning(line, *args, **kwargs)

    warning = w = warn

    def info(self, message, *args, **kwargs):
        for line in str(message).splitlines():
            self.logger.info(line, *args, **kwargs)

    inf = nfo = i = info

    def debug(self, message, *args, **kwargs):
        for line in str(message).splitlines():
            self.logger.debug(line, *args, **kwargs)

    dbg = d = debug

    # other convenience functions to set the global logging level
    def _parse_level(self, lvl):
        for log_level in self.aliases:
            if lvl == log_level or lvl in self.aliases[log_level]:
                return log_level
        print('Invalid log level passed. Please select from debug | info |'
              ' warning | error')
        raise ValueError("{}-Invalid log level.".format(lvl))

    def level(self, lvl=CRITICAL):
        """Setup the Logger."""

        self._lvl = self._parse_level(lvl)
        self.stream = StreamHandler(stream=stdout)
        self.stream.setLevel(self._lvl)

        self.stream.setLevel(self._lvl)

        self.stream.setFormatter(
            ColoredFormatter(self.format, log_colors=self.colors))

        self.logger.setLevel(self._lvl)

        self.logger.addHandler(self.stream)
        root.setLevel(self._lvl)


logger = Log()
