'''Tyke wrapper around OTel MySQL Instrumentor''' 
import logging
from opentelemetry.instrumentation.mysql import MySQLInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class MySQLInstrumentorWrapper(MySQLInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel MySQL Instrumentor class'''
