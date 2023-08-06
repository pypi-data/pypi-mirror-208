'''Tyke wrapper around OTel PyMySQL Instrumentor'''
import logging
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class PyMySQLInstrumentorWrapper(PyMySQLInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel PyMySQL Instrumentor class'''
