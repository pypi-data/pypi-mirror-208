from typing import Callable, Dict, Tuple
from functools import wraps
from opentelemetry.trace import Tracer
from opentelemetry import trace

class TracingDecoratorOptions:
    class NamingSchemes:
        @staticmethod
        def function_qualified_name(func: Callable):
            return func.__qualname__

        default_scheme = function_qualified_name

    naming_scheme: Callable[[Callable], str] = NamingSchemes.default_scheme
    default_attributes: Dict[str, str] = {}

    @staticmethod
    def set_naming_scheme(naming_scheme: Callable[[Callable], str]):
        TracingDecoratorOptions.naming_scheme = naming_scheme

def tyke_instrument(_func=None, *,  span_name: str = "", record_exception: bool = True,
            attributes: Dict[str, str] = None, existing_tracer: Tracer = None):

    def span_decorator(func):
        tracer = existing_tracer or trace.get_tracer(func.__module__)

        def _set_attributes(span, attributes_dict):
            if attributes_dict:
                for att in attributes_dict:
                    span.set_attribute(att, attributes_dict[att])
                    
        @wraps(func)
        def wrap_with_span(*args, **kwargs):
            name = span_name or TracingDecoratorOptions.naming_scheme(func)
            with tracer.start_as_current_span(name, record_exception=record_exception) as span:
                span.set_attribute("method.name", name)
                _set_attributes(span, attributes)
                return func(*args, **kwargs)

        return wrap_with_span

    if _func is None:
        return span_decorator
    else:
        return span_decorator(_func)