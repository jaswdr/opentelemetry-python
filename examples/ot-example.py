import requests
import sys
import time

import opentracing
from opentracing.propagation import Format
from opentracing.ext import tags

from ot_otel_bridge.tracer import tracer

if __name__ == "__main__":
    opentracing.tracer = tracer()

    headers = {}
    with opentracing.tracer.start_active_span('TestSpan') as scope:
        scope.span.set_tag('my_tag_key', 'my_tag_value')
        scope.span.set_baggage_item('my_baggage_item', 'the_baggage')
        scope.span.log_kv({'event': 'string-format', 'value': 'the_log'})
        scope.span.log_event('test message', payload={'life': 42})
        with opentracing.tracer.start_active_span('TestSubSpan') as scope2:
            opentracing.tracer.inject(scope2.span.context, Format.HTTP_HEADERS, headers)
    
    print(headers)
    span_ctx = opentracing.tracer.extract(Format.HTTP_HEADERS, headers)

    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with opentracing.tracer.start_active_span('OtherSide', child_of=span_ctx, tags=span_tags) as scope:
        the_baggage = scope.span.get_baggage_item('my_baggage_item')
        print("The baggage: " + the_baggage)
