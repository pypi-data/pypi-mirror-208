'''Tyke wrapper around OTel Confluent Kafka instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

class ConfluentKafkaInstrumentorWrapper(ConfluentKafkaInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Confluent Kafka instrumentor class'''

