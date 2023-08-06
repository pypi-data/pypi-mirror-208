# -*- coding: utf-8 -*-

import logging
import time

from monkey.crawler.op_codes import OpCode


class RecoverableError(Exception):

    def __init__(self, message='Recoverable error', cause=None):
        self.message = message
        self.cause = cause


class InputError(Exception):

    def __init__(self, record_info, explanation='', cause=None):
        self.message = f'Bad input for record: {record_info} -> {explanation}'
        self.record_info = record_info
        self.cause = cause


class ProcessingError(Exception):
    def __init__(self, record_info, explanation='', cause=None):
        self.message = f'{explanation} -> {cause}\n\t{record_info}'
        self.record_info = record_info
        self.cause = cause


class Handler:
    """Supports misc operation to prepare record for processing.  This may include validation, formatting, projection
    (reduction), enrichment, flattening, transformation, calculation, etc."""

    def __init__(self):
        self.logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')

    def handle(self, record: dict, op_code: OpCode = None) -> (dict, OpCode):
        """Performs an operation on the supplied record in preparation for processing
        :param record: the record to handle
        :param op_code: the operation code computed by any previous operation
        :return: a new record resulting of the operation run
        :return: a computed operation code that can influence the global processing of the record
        """
        raise NotImplemented()


class Processor:
    def __init__(self, name: str = None):
        self.logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self.name = self.__class__.__name__ if (name is None or len(name.strip()) == 0) else name
        self._start_time = 0
        self._end_time = 0

    def __enter__(self):
        self._end_time = 0
        self._start_time = time.time()
        self._enter()
        return self

    def _enter(self):
        raise NotImplementedError()

    def __exit__(self, *args):
        self._end_time = time.time()
        self._exit()
        return False

    def _exit(self):
        raise NotImplementedError()

    def process(self, record):
        return self._process(record)

    def _process(self, record):
        """Actual processing of a handled objet
        :param record: The record object to process
        :return: The executed operation code
        """
        raise NotImplemented()

    def get_processing_duration(self):
        if self._start_time > 0:
            if self._end_time > 0:
                return self._end_time - self._start_time
            else:
                return time.time() - self._start_time
        else:
            return 0
