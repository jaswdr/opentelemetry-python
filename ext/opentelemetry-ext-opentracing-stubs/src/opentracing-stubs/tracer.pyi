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

from typing import Any, Dict, List, Optional, Union

from opentracing import Reference, Scope, ScopeManager, Span, SpanContext

class Tracer(object):
    def __init__(
        self, scope_manager: Optional[ScopeManager] = ...
    ) -> None: ...
    @property
    def scope_manager(self) -> ScopeManager: ...
    @property
    def active_span(self) -> Span: ...
    def start_active_span(
        self,
        operation_name: str,
        child_of: Optional[Union[Span, SpanContext]] = ...,
        references: Optional[List[Reference]] = ...,
        tags: Optional[Dict[str, Union[str, bool, int, float]]] = ...,
        start_time: Optional[float] = ...,
        ignore_active_span: Optional[bool] = ...,
        finish_on_close: bool = ...,
    ) -> Scope: ...
    def start_span(
        self,
        operation_name: str,
        child_of: Optional[Union[Span, SpanContext]] = ...,
        references: Optional[List[Reference]] = ...,
        tags: Optional[Dict[str, Union[str, bool, int, float]]] = ...,
        start_time: Optional[float] = ...,
        ignore_active_span: Optional[bool] = ...,
    ) -> Span: ...
    def inject(
        self, span_context: SpanContext, format: Any, carrier: Any
    ) -> None: ...
    def extract(self, format: Any, carrier: Any) -> SpanContext: ...
