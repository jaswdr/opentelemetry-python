# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from threading import Lock
import time

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import Span as OtelSpan

from .context import BridgeSpanContext


class BridgeSpan():
    def __init__(
        self,
        otel_context,
        otel_span,
    ):
        self._lock = Lock()
        self.logs = []

        self._context = BridgeSpanContext(otel_context=otel_context)
        self.otel_span = otel_span

    @property
    def context(self):
        return self._context

    def set_operation_name(self, operation_name):
        self.otel_span.update_name(operation_name)

    def set_tag(self, key, value):
        self.otel_span.set_attribute(key, value)

    def log_event(self, event, payload=None):
        """DEPRECATED"""
        if payload is None:
            return self.log_kv({'event': event})
        else:
            return self.log_kv({'event': event, 'payload': payload})

    def log_kv(self, key_values, timestamp=None):
        with self._lock:
            self.logs.append((key_values, time.time() if timestamp is None else timestamp))
        return self

    def finish(self, finish_time=None):
        pass  # FIXME

    def set_baggage_item(self, key, value):
        # FIXME
        return self

    def get_baggage_item(self, key):
        # FIXME
        return None
