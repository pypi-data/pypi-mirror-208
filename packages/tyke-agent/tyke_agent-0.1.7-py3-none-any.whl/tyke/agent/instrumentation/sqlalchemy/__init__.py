'''Tyke wrapper around OTel SQLAlchemy Instrumentor'''
import logging
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class SQLAlchemyInstrumentorWrapper(SQLAlchemyInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel SQLAlchemy Instrumentor class'''
