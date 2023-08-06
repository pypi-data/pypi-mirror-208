'''Tyke wrapper around OTel URLLib3 Instrumentor'''
import logging
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class URLLib3InstrumentorWrapper(URLLib3Instrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel URLLib3 Instrumentor class'''
