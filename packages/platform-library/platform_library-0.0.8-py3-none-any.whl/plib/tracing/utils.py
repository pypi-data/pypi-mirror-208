from typing import Optional

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace import Tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import plib.tracing as pt


def get_tracer(tracer_name: Optional[str] = __name__) -> Optional[Tracer]:
    """
    Return Tracer object if tracing flag is True else return None

    Parameters
    ----------
    tracer_name: str
        The uniquely identifiable name for instrumentation scope, such as instrumentation library, package,
        module or class name.

    Returns
    -------
    Tracer:
        Tracer objects which is the interface for sending traces
    """
    if pt.TRACING_ENABLED:
        return trace.get_tracer(tracer_name)
    else:
        return None


def get_current_tracing_context() -> dict:
    """
    Use in service from which you want to SEND request with trace info

    Returns a dictionary that contains information about the current trace_id and span_id.
    Can be used to enrich query headers for example headers.update(tracing_context)

    Returns
    -------
    dict:
        Dictionary with tracing context
    """

    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    return carrier


def extract_tracing_info_from_dict(dictionary: dict) -> Context:
    """
    Get context info from dictionary

    Use in service from which you want to GET request with trace info

    Returns
    -------
    dictionary:
        Dictionary that have tracing info
    """

    return TraceContextTextMapPropagator().extract(dictionary)


def get_top_context_from_request(request) -> Context:
    """
    Get context info from request headers

    Use in service from which you want to GET request with trace info


    Returns
    -------
    request:
        Request object that have headers by request.headers
    """
    return extract_tracing_info_from_dict(request.headers)


def get_top_context_from_info(info) -> Context:
    """
    Get context info from graphene info

    Use in service from which you want to GET request with trace info

    Returns
    -------
    info:
        Request object that have headers info.context.headers
    """
    return extract_tracing_info_from_dict(info.context.headers)


class ContextStub:
    """
    A stub to make the code work properly when tracing is turned off. Fox example:

    'with tracer.start_as_current_span("authorization_extension") if tracer else ContextStub() as span:'

    Returns
    -------
    SpanStub:
        Object that have stubs for record_exception set_attribute set_status methods
    """

    class SpanStub:
        def record_exception(self, *args, **kwargs):
            pass

        def set_attribute(self, *args, **kwargs):
            pass

        def set_status(self, *args, **kwargs):
            pass

    def __enter__(self) -> SpanStub:
        return self.SpanStub()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
