# See LICENSE.incore for details

import logging
import colorlog


# Filter for logs from yapsy module
class yapsy_filter(logging.Filter):
    """
    This class implemets a subclass of the Filter() class of logging
    and helps us filter out the logs generated from the yapsy plugin manager
    package. These errors are (currently) irrelevent to the operation of UATG.
    Hence, we filter these log statements.
    """

    def filter(self, log):
        if '<LogRecord: yapsy,' in str(log.getMessage):
            return 0
        return 1


class Log:
    """
    this class holds all the logic; see the end of the script to
    see how it's instantiated in order to have the line
    "from zenlog import log" work
    """

    aliases = {
        logging.CRITICAL: ("critical", "crit", "fatal"),
        logging.ERROR: ("error", "err"),
        logging.WARNING: ("warning", "warn"),
        logging.INFO: ("info", "inf"),
        logging.DEBUG: ("debug", "dbg")
    }

    def __init__(self, format=None):
        if not format:
            format = "%(log_color)s%(levelname)8s%(reset)s |" \
                     " %(log_color)s%(message)s%(reset)s"
        self.format = format
        self.colors = {
            'DEBUG': 'purple',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red',
        }
        self.logger = logging.getLogger()
        self._lvl = None
        self.stream = None

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
        print('Invalid log level passed. Please select from debug '
              '| info | warning | error')
        raise ValueError("{}-Invalid log level.".format(lvl))

    def level(self, lvl=logging.CRITICAL):
        """Setup the Logger."""

        self._lvl = self._parse_level(lvl)

        self.stream = logging.StreamHandler()
        self.stream.setLevel(self._lvl)

        self.stream.setLevel(self._lvl)

        self.stream.setFormatter(
            colorlog.ColoredFormatter(self.format, log_colors=self.colors))

        # Adding our filter to the Handler.
        self.stream.addFilter(yapsy_filter())

        self.logger.setLevel(self._lvl)

        self.logger.addHandler(self.stream)
        logging.root.setLevel(self._lvl)


logger = Log()
