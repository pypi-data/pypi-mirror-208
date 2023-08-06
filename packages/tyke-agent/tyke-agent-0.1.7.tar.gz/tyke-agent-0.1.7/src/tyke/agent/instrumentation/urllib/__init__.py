'''Tyke wrapper around OTel URLLib Instrumentor'''
import logging
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class URLLibInstrumentorWrapper(URLLibInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel URLLib Instrumentor class'''
