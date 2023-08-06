'''Tyke wrapper around OTel Sklearn Instrumentor'''
import logging
from opentelemetry.instrumentation.sklearn import SklearnInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class SklearnInstrumentorWrapper(SklearnInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Sklearn Instrumentor class'''
