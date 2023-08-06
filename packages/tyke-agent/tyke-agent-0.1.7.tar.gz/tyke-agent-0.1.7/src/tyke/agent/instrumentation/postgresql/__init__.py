'''Tyke wrapper around OTel postgresql instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class PostgreSQLInstrumentorWrapper(Psycopg2Instrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel postgresql instrumentor class'''
    # Psycopg2Instrumentor().instrument(enable_commenter=True, commenter_options={})

