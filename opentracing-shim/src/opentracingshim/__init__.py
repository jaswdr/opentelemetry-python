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

from opentelemetry.trace import Span, SpanContext, Tracer
import opentracing
from contextlib import contextmanager


def create_tracer(tracer: Tracer) -> opentracing.Tracer:
    return TracerWrapper(tracer)


class SpanContextWrapper(opentracing.SpanContext):
    def __init__(self, otel_context: SpanContext):
        self._otel_context = otel_context

    @property
    def otel_context(self):
        return self._otel_context

    @property
    def baggage(self):
        """
        Return baggage associated with this :class:`SpanContext`.
        If no baggage has been added to the :class:`Span`, returns an empty
        dict.

        The caller must not modify the returned dictionary.

        See also: :meth:`Span.set_baggage_item()` /
        :meth:`Span.get_baggage_item()`

        :rtype: dict
        :return: baggage associated with this :class:`SpanContext` or ``{}``.
        """
        return {}
        # TODO: Implement.


class SpanWrapper(opentracing.Span):
    # def __init__(self, tracer, context):
    #     self._tracer = tracer
    #     self._context = context
    def __init__(self, span: Span):
        self._otel_span = span
        # TODO: Finish initialization.

    @property
    def otel_span(self):
        """Returns the OpenTelemetry span embedded in the SpanWrapper."""
        return self._otel_span

    @property
    def context(self):
        # return self._context
        pass
        # TODO: Implement.

    @property
    def tracer(self):
        # return self._tracer
        pass
        # TODO: Implement.

    def set_operation_name(self, operation_name):
        self._otel_span.update_name(operation_name)
        return self

    def finish(self, finish_time=None):
        pass
        # TODO: Implement.

    def set_tag(self, key, value):
        self._otel_span.set_attribute(key, value)

    def log_kv(self, key_values, timestamp=None):
        return self
        # TODO: Implement.

    def set_baggage_item(self, key, value):
        return self
        # TODO: Implement.

    def get_baggage_item(self, key):
        return None
        # TODO: Implement.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Span._on_error(self, exc_type, exc_val, exc_tb)
        # self.finish()
        pass
        # TODO: Implement.

    def log_event(self, event, payload=None):
        # """DEPRECATED"""
        # if payload is None:
        #     return self.log_kv({logs.EVENT: event})
        # else:
        #     return self.log_kv({logs.EVENT: event, 'payload': payload})
        pass
        # TODO: Implement.

    def log(self, **kwargs):
        # """DEPRECATED"""
        # key_values = {}
        # if logs.EVENT in kwargs:
        #     key_values[logs.EVENT] = kwargs[logs.EVENT]
        # if 'payload' in kwargs:
        #     key_values['payload'] = kwargs['payload']
        # timestamp = None
        # if 'timestamp' in kwargs:
        #     timestamp = kwargs['timestamp']
        # return self.log_kv(key_values, timestamp)
        pass
        # TODO: Implement.


class ScopeWrapper(opentracing.Scope):
    def __init__(self, manager, span):
        self._manager = manager
        self._span = span

    @property
    def span(self):
        return self._span

    @property
    def manager(self):
        return self._manager

    def close(self):
        pass
        # TODO: Implement.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # SpanWrapper._on_error(self.span, exc_type, exc_val, exc_tb)
        # self.close()
        pass
        # TODO: Implement.


class TracerWrapper(opentracing.Tracer):
    def __init__(self, tracer: Tracer):
        self._otel_tracer = tracer
        # TODO: Finish implementation.

    @property
    def scope_manager(self):
        # return self._scope_manager
        pass
        # TODO: Implement.

    @property
    def active_span(self):
        # scope = self._scope_manager.active
        # return None if scope is None else scope.span
        pass
        # TODO: Implement.

    @contextmanager
    def start_active_span(
        self,
        operation_name,
        child_of=None,
        references=None,
        tags=None,
        start_time=None,
        ignore_active_span=False,
        finish_on_close=True,
    ) -> ScopeWrapper:
        # TODO: Handle optional arguments.
        with self._otel_tracer.start_span(operation_name) as span:
            yield ScopeWrapper(opentracing.ScopeManager, SpanWrapper(span))

    def start_span(
        self,
        operation_name=None,
        child_of=None,
        references=None,
        tags=None,
        start_time=None,
        ignore_active_span=False,
    ) -> SpanWrapper:
        # TODO: Handle optional arguments.
        parent = child_of
        if parent is not None:
            parent = child_of.otel_span

        span = self._otel_tracer.create_span(operation_name, parent)
        span.start()
        return SpanWrapper(span)

    def inject(self, span_context, format, carrier):
        # if format in Tracer._supported_formats:
        #     return
        # raise UnsupportedFormatException(format)
        pass
        # TODO: Implement.

    def extract(self, format, carrier):
        # if format in Tracer._supported_formats:
        #     return self._noop_span_context
        # raise UnsupportedFormatException(format)
        pass
        # TODO: Implement.
