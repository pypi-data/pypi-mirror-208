# -*- coding: utf-8 -*-

import logging


class Crawler:

    def __init__(self, source_name: str, default_offset: int = 0):
        self.logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self.source_name = source_name
        self.default_offset = default_offset

    def get_records(self, offset: int = 0):
        offset = self.default_offset + offset
        return self._get_records(offset)

    def _get_records(self, offset: int = 0):
        """Returns an iterator on records"""
        raise NotImplementedError()

    def get_start_message(self):
        return self._get_start_message()

    def _get_start_message(self):
        return f'Starts crawling {self.source_name}'


class Accumulator:

    def __init__(self):
        pass

    def __iter__(self):
        raise NotImplementedError()


class InMemoryAccumulator:

    def __init__(self):
        super().__init__()
        self._list = []

    def __iter__(self):
        return self._list.__iter__()

    def add(self, elt):
        self._list.append(elt)

    def __len__(self):
        return len(self._list)
