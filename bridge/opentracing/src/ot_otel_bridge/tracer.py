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


"""
OpenTracing bridge: an OpenTracing tracer implementation using the
OpenTelemetry API.
"""

import time

from opentelemetry.context.propagation import HTTPTextFormat

# FIXME: don't hardcode the choice of b3
import opentelemetry.sdk.context.propagation.b3_format as b3_format

from .span import BridgeSpan
from .scope import BridgeScope
from .context import BridgeSpanContext


def create_tracer(otel_tracer):
    return _BridgeTracer(otel_tracer=otel_tracer)


class _BridgeTracer():
    def __init__(self, otel_tracer):
        """Initialize the bridge Tracer."""
        self._otel_tracer = otel_tracer

        # FIXME: don't hardcode the choice of b3
        self.propagator = b3_format.B3Format()

    def start_active_span(
        self,
        operation_name,
        child_of=None,
        references=None,
        tags=None,
        start_time=None,
        ignore_active_span=False,
        finish_on_close=True,
    ):
        parent=None
        if isinstance(child_of, BridgeSpan):
            parent=child_of.otel_span
        elif isinstance(child_of, BridgeSpanContext):
            parent=child_of.otel_context

        if not ignore_active_span and parent is None:
            parent = self._otel_tracer.get_current_span()

        # # FIXME: cannot use start_span: cannot yield scope without breaking
        # # the OpenTracing API :-(
        # # Unless there is a smart way that I don't see?
        # # Too bad, the code below was working, except that the parent-child
        # # relationship was broken. So instead, I use another hack
        # # see (other FIXME below)

        # with self._otel_tracer.start_span(
        #     name=operation_name,
        #     parent=parent,
        # ) as otel_span:
        #     otel_context = otel_span.get_context()
        #
        #     span = BridgeSpan(
        #         otel_span=otel_span,
        #         otel_context=otel_context,
        #     )
        #
        #     scope = BridgeScope(span)
        #     return scope

        span = self.start_span(
            operation_name,
            child_of,
            references,
            tags,
            start_time,
            ignore_active_span,
        )

        span.otel_span.start()
        # FIXME: hack! hack!
        span_snapshot = self._otel_tracer._current_span_slot.get()
        self._otel_tracer._current_span_slot.set(span.otel_span)

        scope = BridgeScope(self._otel_tracer, span, span_snapshot)
        return scope

    def start_span(
        self,
        operation_name=None,
        child_of=None,
        references=None,
        tags=None,
        start_time=None,
        ignore_active_span=False,
    ):
        parent=None
        if isinstance(child_of, BridgeSpan):
            parent=child_of.otel_span
        elif isinstance(child_of, BridgeSpanContext):
            parent=child_of.otel_context

        if not ignore_active_span and parent is None:
            parent = self._otel_tracer.get_current_span()

        otel_span = self._otel_tracer.create_span(
            name=operation_name,
            parent=parent,
        )
        otel_context = otel_span.get_context()

        return BridgeSpan(
            otel_span=otel_span,
            otel_context=otel_context,
        )

    def inject(self, span_context, format, carrier):
        if format != "http_headers":
            raise Exception("TODO: inject: " + str(format))
            return

        self.propagator.inject(
            span_context.otel_context,
            dict.__setitem__,
            carrier,
        )

    def extract(self, format, carrier):
        if format != "http_headers":
            raise Exception("TODO: extract: " + str(format))
            return

        def get_as_list(dict_object, key):
            value = dict_object.get(key)
            return [value] if value is not None else []

        otel_span_context = self.propagator.extract(get_as_list, carrier)

        return BridgeSpanContext(otel_span_context)
