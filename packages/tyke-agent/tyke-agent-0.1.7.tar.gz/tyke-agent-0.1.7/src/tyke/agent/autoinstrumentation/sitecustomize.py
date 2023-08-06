'''Enable instrumentationon all supported modules.''' # pylint: disable=R0401
import logging
from tyke.agent import Agent
from tyke.env_var_settings import get_env_value

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

skip_modules = get_env_value('SKIP_MODULES')
if skip_modules:
    logger.debug("[env] Loaded SKIP_MODULES from env")
    if len(skip_modules) > 0:
        skip_modules = skip_modules.replace(' ', '')
        skip_modules = skip_modules.split(',')
else:
    skip_modules = []

# Create Tyke agent
agent = Agent()
agent.instrument(None, skip_modules, auto_instrument=True)
