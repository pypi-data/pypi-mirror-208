'''Tyke wrapper around OTel HTTPX Instrumentor''' 
import logging
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class HTTPXInstrumentorWrapper(HTTPXClientInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel httpx Instrumentor class'''
