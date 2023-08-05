import logging
logger = logging.getLogger(__name__)

try:
    import psycopg2
except:
    psycopg2 = None
    logger.warning('psycopg2 not installed')

if psycopg2 is not None:
    from .connection import Connection
    from .structure import *
    from .cmd_gen import diff_to_cmd_list
    from .diff import catalog_diff
    from . import util