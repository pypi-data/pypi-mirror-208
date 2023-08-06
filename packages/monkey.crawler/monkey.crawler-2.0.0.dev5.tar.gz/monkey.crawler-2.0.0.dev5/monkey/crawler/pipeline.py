# -*- coding: utf-8 -*-

import logging
from datetime import datetime

import sys

from monkey.crawler.crawler import Crawler, InMemoryAccumulator
from monkey.crawler.op_codes import OpCode, OpCounter
from monkey.crawler.processor import Processor, Handler, RecoverableError, InputError, ProcessingError


class Pipeline:

    def __init__(self, name: str, crawler: Crawler, handlers: list[Handler], processor: Processor, offset: int = 0,
                 max_retry: int = 0, retry_accumulator=None, reporter=None):
        self.logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self.name = name
        self.crawler = crawler
        self.handlers = [] if handlers is None else handlers
        self.processor = processor
        self.offset = offset
        self.max_retry = max_retry
        self.retry_record_list = []
        self.retry_count = 0
        self.retry_accumulator = InMemoryAccumulator() if retry_accumulator is None else retry_accumulator
        self.reporter = ConsoleReporter() if reporter is None else reporter
        self.activity_logger = ActivityLogger('pipeline')

    def start(self):
        self._start(self.crawler.get_records(self.offset))

    def _start(self, records):
        allow_retry = self.retry_count < self.max_retry
        if self.retry_count == 0:
            self.reporter.echo(self._get_start_message())
            self.reporter.echo(self.crawler.get_start_message())
        self.reporter.pass_start(self.retry_count + 1, self.name)
        counter = OpCounter()
        self._execute(records, allow_retry, counter)
        self.reporter.pass_end(self.retry_count + 1, self.name, self.processor.get_processing_duration())
        if len(self.retry_accumulator) > 0 and allow_retry:
            self.retry_count += 1
            self._start(self.retry_accumulator)
        else:
            self.reporter.final_report(counter)

    def _execute(self, records, allow_retry, counter):
        with self.processor as processor:
            for record in records:
                self.reporter.line_head(counter)
                try:
                    rec, op_code = self._handle(record)
                    if op_code not in (OpCode.IGNORE, OpCode.SKIP, OpCode.ERROR):
                        op_code = processor.process(rec)
                except RecoverableError as e:
                    self.logger.error(f'{self.name} - RECOVERABLE ERROR - {e.message}')
                    if allow_retry:
                        op_code = OpCode.RETRY
                    else:
                        op_code = OpCode.ERROR
                except InputError as e:
                    self.logger.error(f'{self.name} - INPUT ERROR - {e.message}')
                    op_code = OpCode.ERROR
                except ProcessingError as e:
                    self.logger.error(f'{self.name} - PROCESSING ERROR - {e.message}')
                    op_code = OpCode.ERROR
                except Exception as e:
                    self.logger.error(f'{self.name} - UNEXPECTED ERROR - {e}')
                    op_code = OpCode.ERROR
                self.logger.log(op_code.default_logging_level, f'{self.name} - {op_code.name} - {record}')

                counter.inc(op_code)
                self.reporter.plot(op_code)
                self.activity_logger.report(record, op_code)
                if op_code == OpCode.SKIP or op_code == OpCode.RETRY:
                    self.retry_accumulator.add(record)

    def _handle(self, record):
        rec = record
        op_code = None
        for handler in self.handlers:
            handler: Handler
            try:
                rec, op_code = handler.handle(rec, op_code)
                if op_code in (OpCode.IGNORE, OpCode.SKIP, OpCode.ERROR) or rec is None:
                    break
            except ProcessingError as e:
                raise e
            except Exception as e:
                raise ProcessingError(record, f'{type(handler).__name__} failed to handle record', e)
        return rec, op_code

    def _get_start_message(self):
        return f'{self.name} pipeline starts at {datetime.now():%d/%m/%Y %H:%M:%S}'


class ConsoleReporter:
    DEFAULT_MAX_COL = 100

    def __init__(self, out=sys.stdout, max_col: int = DEFAULT_MAX_COL, head_len: int = 6):
        self.out = out
        self.max_col: int = max_col
        self.plot_count: int = 0
        self.head_len: int = head_len

    def _println(self, *objects, sep=' '):
        self._print(*objects, sep=sep, end='\n', flush=False)

    def _print(self, *objects, sep=' ', end='', flush=True):
        print(*objects, sep=sep, end=end, file=self.out, flush=flush)

    def echo(self, message):
        self._println(message)

    def pass_start(self, idx, source_name):
        self._print(f'\n-- START PASS #{idx} ({source_name}) --')

    def pass_end(self, idx, source_name, duration):
        self._println(f'\n-- END PASS #{idx} ({source_name}) -- duration {duration:2f} ms')

    def final_report(self, counter: OpCounter):
        self._println(f'\nCrawling report: \n{counter}')

    def line_head(self, counter: OpCounter):
        if counter.total() % self.max_col == 0:
            self._print(f'\n{self.plot_count:<{self.head_len}}: ')
            self.plot_count += self.max_col

    def plot(self, op_code: OpCode):
        self._print(op_code.plot_symbol)

    def reset(self):
        self.plot_count = 0


class ActivityLogger:

    def __init__(self, base_name: str = None):
        logger_base_name = f'{self.__class__.__module__}.{self.__class__.__name__}' if base_name is None else base_name
        self.loggers = {}
        for op_code in OpCode:
            self.loggers[op_code] = logging.getLogger(f'{logger_base_name}.{op_code.name}')

    def report(self, record, op_code: OpCode, message: str = None):
        logger = self.loggers[op_code]
        extra = {
            'op_code': op_code.name,
            'record': record
        }
        msg = f'{op_code.name} - {record}' if message is None else message
        logger.log(op_code.default_logging_level, msg, extra=extra)
