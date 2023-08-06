'''Tyke wrapper around OTel Remoulade Instrumentor'''
import logging
from opentelemetry.instrumentation.remoulade import RemouladeInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class RemouladeInstrumentorWrapper(RemouladeInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Remoulade Instrumentor class'''
