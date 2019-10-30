from __future__ import print_function


from tornado import gen, ioloop

from ..otel_ot_shim_tracer import MockTracer
from opentracing.scope_managers.tornado import tracer_stack_context
from ..testcase import OpenTelemetryTestCase
from ..utils import stop_loop_when


class TestTornado(OpenTelemetryTestCase):
    def setUp(self):
        self.tracer = MockTracer()
        self.loop = ioloop.IOLoop.current()

    def test_main(self):
        # Start a Span and let the callback-chain
        # finish it when the task is done
        with tracer_stack_context():
            with self.tracer.start_active_span('one', finish_on_close=False):
                self.submit()

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 1)
        self.loop.start()

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].name, 'one')

        for i in range(1, 4):
            self.assertEqual(spans[0].attributes.get('key%s' % i, None), str(i))

    # Since StackContext propagates the active Span
    # from the first callback, we don't need to re-activate
    # it later on anymore.
    @gen.coroutine
    def submit(self):
        span = self.tracer.scope_manager.active.span

        @gen.coroutine
        def task1():
            self.assertEqual(span.unwrap(),
                             self.tracer.scope_manager.active.span.unwrap())
            span.set_tag('key1', '1')

            @gen.coroutine
            def task2():
                self.assertEqual(span.unwrap(),
                                 self.tracer.scope_manager.active.span.unwrap())
                span.set_tag('key2', '2')

                @gen.coroutine
                def task3():
                    self.assertEqual(span.unwrap(),
                                     self.tracer.scope_manager.active.span.unwrap())
                    span.set_tag('key3', '3')
                    span.finish()

                yield task3()

            yield task2()

        yield task1()
