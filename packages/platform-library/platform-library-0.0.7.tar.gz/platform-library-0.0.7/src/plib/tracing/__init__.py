from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Tracer

TRACING_ENABLED = None


def set_tracing_flag(tracing_enabled: bool):
    """
    Set global tracing flag which determines whether tracing is enabled or not

    Parameters
    ----------
    tracing_enabled: bool
        Flag value
    """

    global TRACING_ENABLED
    TRACING_ENABLED = tracing_enabled


class ConnectionManager:
    """
    A class that manages OTLP connections to trace storages

    Methods
    -------
    init_connection(service_name: str, tracer_url: str) -> Optional[Tracer]:
        Link service name to all outgoing traces and
        establish connection to trace storage
    """

    @staticmethod
    def init_connection(service_name: str, tracer_url: str) -> Optional[Tracer]:
        """
        Link service name to all outgoing traces and
        establish connection to trace storage

        Parameters
        ----------
        service_name: str
            The name that will be attached to all outgoing traces, denoting the source of these traces

        tracer_url: str
            Trace storage connection path. For example: http://192.168.1.2:4317

        Returns
        -------
        Tracer:
            Tracer objects which is the interface for sending traces
        """
        if TRACING_ENABLED is None:
            raise Exception(f"Tracing flag must be initialized before using this method."
                            f" It can be initialized by calling 'plib.tracing.set_tracing_flag' method")

        if TRACING_ENABLED:
            resource = Resource(attributes={
                SERVICE_NAME: service_name
            })

            provider = TracerProvider(resource=resource)
            processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=tracer_url, insecure=True))
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)

            return trace.get_tracer(__name__)
        else:
            return None
