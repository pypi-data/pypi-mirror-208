'''Tyke wrapper around OTel AIOPG instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.aiopg import AiopgInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class AioPGInstrumentorWrapper(AiopgInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel AIO PG instrumentor class'''

