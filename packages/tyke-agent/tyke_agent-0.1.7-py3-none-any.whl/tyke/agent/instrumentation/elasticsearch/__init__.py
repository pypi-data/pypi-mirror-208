'''Tyke wrapper around OTel Elasticsearch instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class ElasticsearchInstrumentorWrapper(ElasticsearchInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel AIO Elasticsearch instrumentor class'''

