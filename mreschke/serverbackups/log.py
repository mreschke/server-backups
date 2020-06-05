import logging
import logging.config
import re
import sys
from logging import Formatter

from colored import attr, bg, fg


# Usage: from mreschke.serverbackups import log
# log.init(config_dict)
# log.debug(), log.info()...standard python logging methods
def init(config={}):
    # Default Config
    # Levels = NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    default = {
        'console': {
            'enabled': True,
            'level': 'INFO',
            'colors': True,
            'format': '%(message)s'
        },
        'file': {
            'enabled': False,
            'level': 'INFO',
            'file': '/tmp/example.log',
            'format': '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s'
        }
    }

    # Merge default and user defined config
    config = {**default, **config}
    if 'console' in config.keys(): config['console'] = {**default['console'], **config['console']}
    if 'file' in config.keys(): config['file'] = {**default['file'], **config['file']}

    # New Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # from .env

    # New Console Handler
    if config['console']['enabled']:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(config['console']['level'])
        if config['console']['colors']:
            ch.setFormatter(ColoredFormatter(config['console']['format']))
        else:
            ch.setFormatter(logging.Formatter(
                fmt=config['console']['format'],
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        logger.addHandler(ch)

    # New File Handler
    if config['file']['enabled']:
        fh = logging.FileHandler(filename=config['file']['file'], mode='a')
        fh.setLevel(config['file']['level'])
        fh.setFormatter(logging.Formatter(
            fmt=config['file']['format'],
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(fh)


def debug(message):
    logging.debug(message)


def info(message):
    logging.info(message)


def warning(message):
    logging.warning(message)


def error(message):
    logging.error(message)


def critical(message):
    logging.critical(message)


def exception(message):
    logging.exception(message)


def header(message):
    logging.info(":: " + message + " ::")


def header2(message):
    logging.info("## " + message + " ##")


def header3(message):
    logging.info("=== " + message + " ===")


def header4(message):
    logging.info("---- " + message + " ----")


def bullet(message):
    logging.info("* " + message)


def bullet2(message):
    logging.info("- " + message)


def bullet3(message):
    logging.info("+ " + message)


def bullet4(message):
    logging.info("> " + message)


def notice(message):
    logging.info("NOTICE: " + message)


def blank():
    logging.info('')


def separator():
    logging.info('=' * 80)


def line():
    logging.info('-' * 80)


class ColoredFormatter(Formatter):

    def __init__(self, patern):
        Formatter.__init__(self, patern)

    def format(self, record):
        # Remember this is console output only, not file or other handlers
        # See color chart https://pypi.org/project/colored/
        level = record.levelname
        message = logging.Formatter.format(self, record)

        # Format header
        if (level == 'INFO' and re.match("^:: ", message)):
            message = re.sub("^:: ", "", message)
            message = re.sub(" ::$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ':: ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ::', attr(0))

        # Format header2
        if (level == 'INFO' and re.match("^## ", message)):
            message = re.sub("^## ", "", message)
            message = re.sub(" ##$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '## ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ##', attr(0))

        # Format header3
        if (level == 'INFO' and re.match("^=== ", message)):
            message = re.sub("^=== ", "", message)
            message = re.sub(" ===$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '=== ', attr(0)) \
                + ('{0}{1}{2}').format(fg('green'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ===', attr(0))

        # Format header4
        if (level == 'INFO' and re.match("^---- ", message)):
            message = re.sub("^---- ", "", message)
            message = re.sub(" ----$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '---- ', attr(0)) \
                + ('{0}{1}{2}').format(fg('green'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ----', attr(0))

        # Format bullet * item
        elif (level == 'INFO' and re.match("^\* ", message)):
            message = re.sub("^\* ", "", message)
            message = ('{0}{1}{2}').format(fg('green'), '   * ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet2 - item
        elif (level == 'INFO' and re.match("^- ", message)):
            message = re.sub("^- ", "", message)
            message = ('{0}{1}{2}').format(fg('cyan'), '   - ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet3 + item
        elif (level == 'INFO' and re.match("^\+ ", message)):
            message = re.sub("^\+ ", "", message)
            message = ('{0}{1}{2}').format(fg('red'), '   + ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet4 > item
        elif (level == 'INFO' and re.match("^> ", message)):
            message = re.sub("^> ", "", message)
            message = ('{0}{1}{2}').format(fg('magenta'), '   > ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format notice
        elif (level == 'INFO' and re.match("^NOTICE: ", message)):
            message = re.sub("^NOTICE: ", "", message)
            message = ('{0}{1}{2}{3}').format(fg('yellow'), attr('bold'), 'NOTICE: ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format separator
        elif (level == 'INFO' and re.match("^====", message)):
            message = ('{0}{1}{2}{3}').format(fg('orange_4a'), attr('bold'), message, attr(0))

        # Format line
        elif (level == 'INFO' and re.match("^----", message)):
            message = ('{0}{1}{2}{3}').format(fg('orange_4a'), attr('bold'), message, attr(0))

        elif (level == 'DEBUG'):
            message = ('{0}{1}{2}').format(fg(241), message, attr(0))
        elif (level == 'INFO'):
            message = message
        elif (level == 'WARNING'):
            message = ('{0}{1}{2}').format(fg('orange_red_1'), message, attr(0))
        elif (level == 'ERROR'):
            message = ('{0}{1}{2}').format(fg('red'), message, attr(0))
        elif (level == 'CRITICAL'):
            message = ('{0}{1}{2}{3}').format(fg('white'), bg('red'), message, attr(0))

        return message
