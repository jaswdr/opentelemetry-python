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

import logging

from typing import ContextManager, Dict, Iterator, List, Optional, Union

import opentracing

from opentelemetry import trace
from opentelemetry.ext.opentracing_shim import util

logger = logging.getLogger(__name__)


class SpanContextShim(opentracing.SpanContext):
    def __init__(self, otel_context: trace.SpanContext):
        self._otel_context = otel_context

    def unwrap(self) -> trace.SpanContext:
        """Returns the wrapped OpenTelemetry `SpanContext` object."""

        return self._otel_context

    @property
    def baggage(self) -> Dict[str, str]:
        logger.warning(
            "Using unimplemented property baggage on class %s.",
            self.__class__.__name__,
        )
        return {}
        # TODO: Implement.


class SpanShim(opentracing.Span):
    def __init__(
        self,
        tracer: opentracing.Tracer,
        context: opentracing.SpanContext,
        span: trace.Span,
    ) -> None:
        super().__init__(tracer, context)
        self._otel_span = span

    def unwrap(self) -> trace.Span:
        """Returns the wrapped OpenTelemetry `Span` object."""

        return self._otel_span

    def set_operation_name(self, operation_name: str) -> "SpanShim":
        self._otel_span.update_name(operation_name)

        return self

    def finish(self, finish_time: Optional[float] = None) -> None:
        if finish_time is None:
            end_time = None
        else:
            end_time = util.time_seconds_to_ns(finish_time)
        self._otel_span.end(end_time=end_time)

    def set_tag(
        self, key: str, value: Union[str, bool, int, float]
    ) -> "SpanShim":
        self._otel_span.set_attribute(key, value)

        return self

    def log_kv(
        self,
        key_values: Dict[str, Union[str, bool, float]],
        timestamp: float = None,
    ) -> "SpanShim":
        if timestamp is None:
            event_timestamp = None
        else:
            event_timestamp = util.time_seconds_to_ns(timestamp)
        event_name = util.event_name_from_kv(key_values)
        self._otel_span.add_event(event_name, event_timestamp, key_values)

        return self

    def set_baggage_item(self, key: str, value: str) -> "SpanShim":
        logger.warning(
            "Calling unimplemented method set_baggage_item() on class %s",
            self.__class__.__name__,
        )
        return None  # type: ignore
        # TODO: Implement.

    def get_baggage_item(self, key: str) -> str:
        logger.warning(
            "Calling unimplemented method get_baggage_item() on class %s",
            self.__class__.__name__,
        )
        return ""
        # TODO: Implement.

    # TODO: Verify calls to deprecated methods `log_event()` and `log()` on
    # base class work properly (it's probably fine because both methods call
    # `log_kv()`).


class ScopeShim(opentracing.Scope):
    """A `ScopeShim` wraps the OpenTelemetry functionality related to span
    activation/deactivation while using OpenTracing `Scope` objects for
    presentation.

    There are two ways to construct a `ScopeShim` object: using the `span`
    argument and using the `span_cm` argument. One and only one of `span` or
    `span_cm` must be specified.

    When calling the initializer while passing a `SpanShim` object in the
    `span` argument, the `ScopeShim` is initialized as a regular `Scope`
    object.

    When calling the initializer while passing a context manager *generator* in
    the `span_cm` argument (as returned by the `use_span()` method of
    OpenTelemetry `Tracer` objects,  the resulting `ScopeShim` becomes
    usable as a context manager (using `with` statements).

    It is necessary to have both ways for constructing `ScopeShim`
    objects because in some cases we need to create the object from a context
    manager, in which case our only way of retrieving a `Span` object is by
    calling the `__enter__()` method on the context manager, which makes the
    span active in the OpenTelemetry tracer; whereas in other cases we need to
    accept a `SpanShim` object and wrap it in a `ScopeShim`.
    """

    def __init__(
        self,
        manager: "ScopeManagerShim",
        span: SpanShim,
        span_cm: Iterator[None] = None,
    ) -> None:
        super().__init__(manager, span)
        self._span_cm = span_cm

    # TODO: Change type of `manager` argument to `opentracing.ScopeManager`? We
    # need to get rid of `manager.tracer` for this.
    @classmethod
    def from_context_manager(
        cls, manager: "ScopeManagerShim", span_cm: Iterator[None]
    ) -> "ScopeShim":
        otel_span = span_cm.__enter__()
        span_context = SpanContextShim(otel_span.get_context())
        span = SpanShim(manager.tracer, span_context, otel_span)
        return cls(manager, span, span_cm)

    def close(self) -> None:
        if self._span_cm is not None:
            # We don't have error information to pass to `__exit__()` so we
            # pass `None` in all arguments. If the OpenTelemetry tracer
            # implementation requires this information, the `__exit__()` method
            # on `opentracing.Scope` should be overridden and modified to pass
            # the relevant values to this `close()` method.
            self._span_cm.__exit__(None, None, None)
        else:
            # Required to convince mypy that `self._span` is a `SpanShim`.
            assert isinstance(self._span, SpanShim)
            self._span.unwrap().end()


class ScopeManagerShim(opentracing.ScopeManager):
    def __init__(self, tracer: "TracerShim") -> None:
        super().__init__()
        self._tracer = tracer

    def activate(
        self, span: opentracing.Span, finish_on_close: bool
    ) -> opentracing.Scope:
        if isinstance(span, SpanShim):
            span_cm = self._tracer.unwrap().use_span(
                span.unwrap(), end_on_exit=finish_on_close
            )
            return ScopeShim.from_context_manager(self, span_cm)

        logger.warning("activate() method doesn't support `Span` objects.")
        return self._noop_scope

    @property
    def active(self):
        span = self._tracer.unwrap().get_current_span()
        if span is None:
            return None

        span_context = SpanContextShim(span.get_context())
        wrapped_span = SpanShim(self._tracer, span_context, span)
        return ScopeShim(self, span=wrapped_span)
        # TODO: Return a saved instance of SpanShim instead of constructing
        # a new object (and the same for ScopeShim?).
        # https://github.com/open-telemetry/opentelemetry-python/issues/161#issuecomment-534136274

    @property
    def tracer(self):
        return self._tracer


class TracerShim(opentracing.Tracer):
    def __init__(
        self,
        tracer: trace.Tracer,
        scope_manager: opentracing.ScopeManager = None,
    ) -> None:
        scope_manager = ScopeManagerShim(self)
        super().__init__(scope_manager=scope_manager)
        self._otel_tracer = tracer

    def unwrap(self) -> trace.Tracer:
        """Returns the wrapped OpenTelemetry `Tracer` object."""

        return self._otel_tracer

    def start_active_span(
        self,
        operation_name: str,
        child_of: Optional[
            Union[opentracing.Span, opentracing.SpanContext]
        ] = None,
        references: Optional[List[opentracing.Reference]] = None,
        tags: Optional[Dict[str, Union[str, bool, int, float]]] = None,
        start_time: Optional[float] = None,
        ignore_active_span: Optional[bool] = False,
        finish_on_close: bool = True,
    ) -> opentracing.Scope:
        span = self.start_span(
            operation_name=operation_name,
            child_of=child_of,
            references=references,
            tags=tags,
            start_time=start_time,
            ignore_active_span=ignore_active_span,
        )
        return self._scope_manager.activate(span, finish_on_close)

    def start_span(
        self,
        operation_name=None,
        child_of=None,
        references=None,
        tags=None,
        start_time=None,
        ignore_active_span=False,
    ):
        # Use active span as parent when no explicit parent is specified.
        if not ignore_active_span and not child_of:
            child_of = self.active_span

        # Use the specified parent or the active span if possible. Otherwise,
        # use a `None` parent, which triggers the creation of a new trace.
        parent = child_of.unwrap() if child_of else None
        span = self._otel_tracer.create_span(operation_name, parent)

        if references:
            for ref in references:
                span.add_link(ref.referenced_context.unwrap())

        if tags:
            for key, value in tags.items():
                span.set_attribute(key, value)

        # The OpenTracing API expects time values to be `float` values which
        # represent the number of seconds since the epoch. OpenTelemetry
        # represents time values as nanoseconds since the epoch.
        start_time_ns = start_time
        if start_time_ns is not None:
            start_time_ns = util.time_seconds_to_ns(start_time)

        span.start(start_time=start_time_ns)
        context = SpanContextShim(span.get_context())
        return SpanShim(self, context, span)

    def inject(self, span_context, format, carrier):
        # pylint: disable=redefined-builtin
        logger.warning(
            "Calling unimplemented method inject() on class %s",
            self.__class__.__name__,
        )
        # TODO: Implement.

    def extract(self, format, carrier):
        # pylint: disable=redefined-builtin
        logger.warning(
            "Calling unimplemented method extract() on class %s",
            self.__class__.__name__,
        )
        # TODO: Implement.


def create_tracer(tracer: trace.Tracer) -> TracerShim:
    return TracerShim(tracer)
