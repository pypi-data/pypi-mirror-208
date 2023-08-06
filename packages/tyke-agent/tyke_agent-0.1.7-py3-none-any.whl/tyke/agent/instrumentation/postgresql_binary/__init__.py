'''Tyke wrapper around OTel postgresql-binary instrumentor'''
import sys
import os.path
import logging
import traceback
from typing import Collection
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class PostgreSQLBinaryInstrumentorWrapper(Psycopg2Instrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel postgresql-binary instrumentor class'''
    # Psycopg2Instrumentor().instrument(enable_commenter=True, commenter_options={})

    def instrumentation_dependencies(self) -> Collection[str]:
        return ("psycopg2-binary >= 2.7.3.1",)

