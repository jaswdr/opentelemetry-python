import requests
import sys
import time

import opentracing

from ot_otel_bridge.tracer import Tracer

if __name__ == "__main__":
  opentracing.tracer = Tracer()

  with opentracing.tracer.start_active_span('TestSpan') as scope:
    scope.span.log_event('test message', payload={'life': 42})


