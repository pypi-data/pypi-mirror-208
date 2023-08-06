'''Tyke wrapper around OTel Kafka instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class KafkaInstrumentorWrapper(KafkaInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Kafka instrumentor class'''

