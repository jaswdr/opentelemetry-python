"""
OpenTracing bridge: an OpenTracing tracer implementation using the
OpenTelemetry API.
"""

from basictracer import BasicTracer

def Tracer(**kwargs):
    return _BridgeTracer()

class _BridgeTracer(BasicTracer):
    def __init__(self):
        """Initialize the bridge Tracer."""
        super(_BridgeTracer, self).__init__(recorder=None, scope_manager=None)

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          tags=None,
                          start_time=None,
                          ignore_active_span=False,
                          finish_on_close=True):
        return super(_BridgeTracer, self).start_active_span(
            operation_name, child_of, references, tags, start_time,
            ignore_active_span, finish_on_close)

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None,
                   ignore_active_span=False):
        return super(_BridgeTracer, self).start_span(
            operation_name, child_of, references, tags, start_time,
            ignore_active_span)

    def __enter__(self):
        return self
