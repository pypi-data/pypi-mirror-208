# Tyke Python Agent

Tyke Python agent provides instrumentation for collecting traces data to be processed by [Tyke](https://tyke.ai/).

This agent supports these frameworks and adds following capabilities:

- capture request and response headers
- capture request and response bodies
- capture SQL queries
- tracing context propagation

Tyke python agent supports Python 3.6+

| Library | Description | Supported Library Versions|
|------|-------------| ---------------|
| [flask](https://flask.palletsprojects.com/en/1.1.x/api)|A micro web framework written in Python.| 1.\*, 2.\*|
| [django](https://docs.djangoproject.com/)|Python web framework | 1.10+|
| [grpc](https://grpc.github.io/grpc/python/)|Python GRPC library.| 1.27+|
| [mysql-connector](https://dev.mysql.com/doc/connector-python/en/)| Python MySQL database client library.| 8.\*|
| [psycopg2/psycopg2-binary/postgresql](https://www.psycopg.org/docs/)|Python Postgresql database client library. | 2.7.3.1+ |
| [requests](https://docs.python-requests.org/en/master/)|Python HTTP client library.| 2.\*|
| [aiohttp](https://docs.aiohttp.org/en/stable/)|Python async HTTP client library.| 3.\*|
| [pymongo](https://pymongo.readthedocs.io/en/stable/)|Python mongodb pymongo library.| >= 3.1+, < 5.0|

## Getting started

## Instrumentation

Instrumentation requires editing your code to initialize an agent, and registering any applicable modules to be instrumented.

- Install the tyke python agent:

```bash
pip install tyke-agent
```

- Create a YAML file with the name config.yaml in the application root directory and add below content

```yaml
    service_name: "Service Name"
    resource_attributes: 
        app.name: "Application Name"
        service.identifier: Service unique identifier

    reporting:
        endpoint: http://localhost:4317
```


- Add the following to your app's entrypoint python file:

```python
from tyke.agent import Agent

agent = Agent() # initialize the agent

# Instrument a specific flask app + any other applicable libraries
agent.instrument(app)

# Instrument a flask app, additional libraries, except for mysql
# the second argument tells the agent to skip these specific libraries from being instrumented
agent.instrument(app, ['mysql'])


# if you aren't using flask, you can pass None
# and still provide skip libraries if needed
agent.instrument(None, ['flask', 'mysql'])

# Set config file location in environment variables 
os.environ.setdefault("TYKE_CONFIG_FILE", "config.yaml")
...
```
