'''Tyke wrapper around OTel PyMongo Instrumentor''' 
import logging
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class PymongoInstrumentorWrapper(PymongoInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel PyMongo Instrumentor class'''
