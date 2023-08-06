'''Tyke wrapper around OTel Celery Instrumentor'''
import logging
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class CeleryInstrumentorWrapper(CeleryInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Celery Instrumentor class'''
