'''Tyke wrapper around OTel postgresql instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

class AsyncPGInstrumentorWrapper(AsyncPGInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel async postgresql instrumentor class'''
    # Psycopg2Instrumentor().instrument(enable_commenter=True, commenter_options={})

