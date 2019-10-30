from __future__ import print_function


import gevent

from ..otel_ot_shim_tracer import MockTracer
from ..testcase import OpenTelemetryTestCase


class TestGevent(OpenTelemetryTestCase):
    def setUp(self):
        self.tracer = MockTracer()

    def test_main(self):
        # Start a Span and let the callback-chain
        # finish it when the task is done
        with self.tracer.start_active_span('one', finish_on_close=False):
            self.submit()

        gevent.wait()

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].name, 'one')

        for i in range(1, 4):
            self.assertEqual(spans[0].attributes.get('key%s' % i, None), str(i))

    def submit(self):
        span = self.tracer.scope_manager.active.span

        def task1():
            with self.tracer.scope_manager.activate(span, False):
                span.set_tag('key1', '1')

                def task2():
                    with self.tracer.scope_manager.activate(span, False):
                        span.set_tag('key2', '2')

                        def task3():
                            with self.tracer.scope_manager.activate(span,
                                                                    True):
                                span.set_tag('key3', '3')

                        gevent.spawn(task3)

                gevent.spawn(task2)

        gevent.spawn(task1)
