"""Tests whether the log can be written to"""

from neopolitan.log import init_logger, get_logger

def test_log():
    """Initializes the logger and writes to it"""

    # todo: doesn't do anything in pytest fixture
    init_logger()
    logger = get_logger()
    logger.debug('DEBUG')
    logger.info('INFO')
    logger.error('ERROR')
