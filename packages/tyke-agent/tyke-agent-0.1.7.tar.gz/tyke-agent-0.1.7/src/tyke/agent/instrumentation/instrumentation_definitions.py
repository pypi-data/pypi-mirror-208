'''this module acts as a driver for instrumentation definitions + application'''
import logging

FLASK_KEY = 'flask'
DJANGO_KEY = 'django'
FAST_API_KEY = 'fastapi'
GRPC_SERVER_KEY = 'grpc:server'
GRPC_CLIENT_KEY = 'grpc:client'
POSTGRESQL_KEY = 'postgresql'
POSTGRESQL_BINARY_KEY = 'postgresql-binary'
MYSQL_KEY = 'mysql'
REQUESTS_KEY = 'requests'
AIOHTTP_CLIENT_KEY = 'aiohttp:client'
LAMBDA = 'lambda'
BOTO = 'boto'
BOTOCORE = 'botocore'

PYMONGO = 'pymongo'
CELERY = 'celery'
ASYNCPG = 'asyncpg'
AIOPG = 'aiopg'
CONFLUENT_KAFKA = 'confluent-kafka'
KAFKA = 'kafka'
ELASTICSEARCH = 'elasticsearch'
HTTPX = 'httpx'
PYMYSQL = 'pymysql'
REDIS = 'redis'
REMOULADE = 'remoulade'
SKLEARN = 'sklearn'
SQLALCHEMY = 'sqlalchemy'
URLLIB3 = 'urllib3'
URLLIB = 'urllib'

SUPPORTED_LIBRARIES = [
    FLASK_KEY, DJANGO_KEY, FAST_API_KEY, GRPC_SERVER_KEY, GRPC_CLIENT_KEY,
    POSTGRESQL_KEY, POSTGRESQL_BINARY_KEY, MYSQL_KEY,REQUESTS_KEY, AIOHTTP_CLIENT_KEY,LAMBDA, BOTO, BOTOCORE, 
    PYMONGO, CELERY, ASYNCPG, AIOPG, CONFLUENT_KAFKA, KAFKA, ELASTICSEARCH, HTTPX,
    PYMYSQL, REDIS, REMOULADE, SKLEARN, SQLALCHEMY, URLLIB3, URLLIB
]

# map of library_key => instrumentation wrapper instance
_INSTRUMENTATION_STATE = {}

logger = logging.getLogger(__name__)

def _uninstrument_all():
    for key in _INSTRUMENTATION_STATE:
        logger.debug("Uninstrumenting %s", key)
        _INSTRUMENTATION_STATE[key].uninstrument()

    _INSTRUMENTATION_STATE.clear()

def is_already_instrumented(library_key):
    """check if an instrumentation wrapper is already registered"""
    return library_key in _INSTRUMENTATION_STATE.keys()


def _mark_as_instrumented(library_key, wrapper_instance):
    """mark an instrumentation wrapper as registered"""
    _INSTRUMENTATION_STATE[library_key] = wrapper_instance


def get_instrumentation_wrapper(library_key): 
    """load an initialize an instrumentation wrapper"""
    if is_already_instrumented(library_key):
        return None
    try:
        wrapper_instance = None
        if DJANGO_KEY == library_key:
            from tyke.agent.instrumentation.django import DjangoInstrumentationWrapper  
            wrapper_instance = DjangoInstrumentationWrapper()
        elif FLASK_KEY == library_key:
            from tyke.agent.instrumentation.flask import FlaskInstrumentorWrapper 
            wrapper_instance = FlaskInstrumentorWrapper()
        elif FAST_API_KEY == library_key:
            from tyke.agent.instrumentation.fast_api import FastAPIInstrumentorWrapper 
            wrapper_instance = FastAPIInstrumentorWrapper()
        elif GRPC_SERVER_KEY == library_key:
            from tyke.agent.instrumentation.grpc import GrpcInstrumentorServerWrapper 
            wrapper_instance = GrpcInstrumentorServerWrapper()
        elif GRPC_CLIENT_KEY == library_key:
            from tyke.agent.instrumentation.grpc import GrpcInstrumentorClientWrapper 
            wrapper_instance = GrpcInstrumentorClientWrapper()
        elif POSTGRESQL_KEY == library_key:
            from tyke.agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper 
            wrapper_instance =  PostgreSQLInstrumentorWrapper()
        elif POSTGRESQL_BINARY_KEY == library_key: 
            from tyke.agent.instrumentation.postgresql_binary import PostgreSQLBinaryInstrumentorWrapper 
            wrapper_instance =  PostgreSQLBinaryInstrumentorWrapper()
        elif MYSQL_KEY == library_key:
            from tyke.agent.instrumentation.mysql import MySQLInstrumentorWrapper 
            wrapper_instance = MySQLInstrumentorWrapper()
        elif REQUESTS_KEY == library_key:
            from tyke.agent.instrumentation.requests import RequestsInstrumentorWrapper 
            wrapper_instance = RequestsInstrumentorWrapper()
        elif AIOHTTP_CLIENT_KEY == library_key:
            from tyke.agent.instrumentation.aiohttp import AioHttpClientInstrumentorWrapper 
            wrapper_instance = AioHttpClientInstrumentorWrapper()
        elif LAMBDA == library_key:
            from tyke.agent.instrumentation.aws_lambda import AwsLambdaInstrumentorWrapper 
            wrapper_instance = AwsLambdaInstrumentorWrapper()
        elif BOTO == library_key:
            from tyke.agent.instrumentation.boto import BotoInstrumentationWrapper 
            wrapper_instance = BotoInstrumentationWrapper()
        elif BOTOCORE == library_key:
            from tyke.agent.instrumentation.botocore import BotocoreInstrumentationWrapper 
            wrapper_instance = BotocoreInstrumentationWrapper()
        elif PYMONGO == library_key:
            from tyke.agent.instrumentation.pymongo import PymongoInstrumentorWrapper 
            wrapper_instance = PymongoInstrumentorWrapper()
        elif CELERY == library_key:
            from tyke.agent.instrumentation.celery import CeleryInstrumentorWrapper 
            wrapper_instance = CeleryInstrumentorWrapper()
        elif PYMYSQL == library_key:
            from tyke.agent.instrumentation.pymysql import PyMySQLInstrumentorWrapper 
            wrapper_instance = PyMySQLInstrumentorWrapper()
        elif REDIS == library_key:
            from tyke.agent.instrumentation.redis import RedisInstrumentorWrapper 
            wrapper_instance = RedisInstrumentorWrapper()
        elif KAFKA == library_key:
            from tyke.agent.instrumentation.kafka_python import KafkaInstrumentorWrapper 
            wrapper_instance = KafkaInstrumentorWrapper()
        elif CONFLUENT_KAFKA == library_key:
            from tyke.agent.instrumentation.confluent_kafka import ConfluentKafkaInstrumentorWrapper 
            wrapper_instance = ConfluentKafkaInstrumentorWrapper()
        elif ASYNCPG == library_key:
            from tyke.agent.instrumentation.asyncpg import AsyncPGInstrumentorWrapper 
            wrapper_instance = AsyncPGInstrumentorWrapper()
        elif AIOPG == library_key:
            from tyke.agent.instrumentation.aiopg import AioPGInstrumentorWrapper 
            wrapper_instance = AioPGInstrumentorWrapper()
        elif ELASTICSEARCH == library_key:
            from tyke.agent.instrumentation.elasticsearch import ElasticsearchInstrumentorWrapper 
            wrapper_instance = ElasticsearchInstrumentorWrapper()
        elif HTTPX == library_key:
            from tyke.agent.instrumentation.httpx import HTTPXInstrumentorWrapper 
            wrapper_instance = HTTPXInstrumentorWrapper()
        elif URLLIB3 == library_key:
            from tyke.agent.instrumentation.urllib3 import URLLib3InstrumentorWrapper 
            wrapper_instance = URLLib3InstrumentorWrapper()
        elif URLLIB == library_key:
            from tyke.agent.instrumentation.urllib import URLLibInstrumentorWrapper 
            wrapper_instance = URLLibInstrumentorWrapper()
        elif SQLALCHEMY == library_key:
            from tyke.agent.instrumentation.sqlalchemy import SQLAlchemyInstrumentorWrapper 
            wrapper_instance = SQLAlchemyInstrumentorWrapper()
        elif SKLEARN == library_key:
            from tyke.agent.instrumentation.sklearn import  SklearnInstrumentorWrapper 
            wrapper_instance = SklearnInstrumentorWrapper()
        elif REMOULADE == library_key:
            from tyke.agent.instrumentation.remoulade import RemouladeInstrumentorWrapper 
            wrapper_instance = RemouladeInstrumentorWrapper()
        else:
            return None

        _mark_as_instrumented(library_key, wrapper_instance)
        return wrapper_instance
    except Exception as _err: # pylint:disable=W0703
        logger.debug("Error while attempting to load instrumentation wrapper for %s", library_key)
        return None
