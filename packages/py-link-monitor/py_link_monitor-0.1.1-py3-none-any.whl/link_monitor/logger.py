import logging
import sys

LOG_FORMAT = '%(name)s %(message)s'

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format=LOG_FORMAT
)

logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

info = logger.info
debug = logger.debug
error = logger.error
