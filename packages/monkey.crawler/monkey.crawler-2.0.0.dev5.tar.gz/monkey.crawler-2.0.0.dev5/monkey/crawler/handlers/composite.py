# -*- coding: utf-8 -*-

from monkey.crawler.op_codes import OpCode
from monkey.crawler.processor import Handler, ProcessingError

_KEEP_STRATEGY: str = "KEEP"
_LAST_COMPUTED_STRATEGY: str = "LAST COMPUTED"


class CompositeHandler(Handler):
    """Executes a handler chain using a configurable strategy for record and operation code"""

    def __init__(self, handlers: list, record_strategy: str = _KEEP_STRATEGY,
                 op_code_strategy: str = _LAST_COMPUTED_STRATEGY):
        """Initializes the handler.
        :param handlers:
        :param record_strategy:
        :param op_code_strategy:
        """
        super().__init__()
        self.handlers = [] if handlers is None else handlers
        self.record_strategy = record_strategy
        self.op_code_strategy = op_code_strategy

    def handle(self, record: dict, op_code: OpCode = None) -> (dict, OpCode):
        """Performs the validation check on target fields from the provided record.
        :param record: the record to validate
        :param op_code: the operation code computed by any previous operation
        :return: a new record resulting of the operation run
        :return: a computed operation code that can influence the global processing of the record
        """
        rec = record
        new_op_code = op_code
        for handler in self.handlers:
            handler: Handler
            try:
                rec, new_op_code = handler.handle(rec, new_op_code)
                if op_code in (OpCode.IGNORE, OpCode.SKIP, OpCode.ERROR) or rec is None:
                    break
            except ProcessingError as e:
                raise e
            except Exception as e:
                raise ProcessingError(record, f'{type(handler).__name__} failed to handle record', e)
        if self.record_strategy == _KEEP_STRATEGY:
            rec = record
        if self.op_code_strategy == _KEEP_STRATEGY:
            new_op_code = op_code
        return rec, new_op_code
