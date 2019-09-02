from basictracer.span import BasicSpan

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import Span as OtelSpan


class BridgeSpan(BasicSpan):
    def __init__(
        self,
        tracer,
        operation_name=None,
        context=None,
        parent_id=None,
        tags=None,
        start_time=None,
        otel_parent=None,
    ):
        super(BridgeSpan, self).__init__(
            tracer, operation_name, context, parent_id, tags, start_time
        )

        otel_context = trace_api.SpanContext(context.trace_id, context.span_id)
        if otel_parent is None:
            otel_parent = trace_api.SpanContext(context.trace_id, parent_id)
        otel_tags = tags

        self.otel_span = OtelSpan(
            name=operation_name,
            context=otel_context,
            parent=otel_parent,
            attributes=otel_tags,
        )

    def set_operation_name(self, operation_name):
        super(BridgeSpan, self).set_operation_name(operation_name)
        self.otel_span.update_name(operation_name)

    def set_tag(self, key, value):
        super(BridgeSpan, self).set_tag(key, value)
        self.otel_span.set_attribute(key, value)
