# -*- coding: utf-8 -*-

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from monkey.crawler.crawler import Crawler

TAG_KEY: str = 'tag'
TEXT_KEY: str = 'text'
TAIL_KEY: str = 'tail'
ATTRIBUTES_KEY: str = 'attributes'
CHILDREN_KEY: str = 'children'


class XMLRecordBuilder:

    def build(self, element: Element):
        raise NotImplemented()


class DefaultXMLRecordBuilder(XMLRecordBuilder):

    def __init__(self, minimize: bool = False):
        super().__init__()
        self.minimize = minimize

    def build(self, element: Element):
        record: dict = {TAG_KEY: element.tag}
        attributes = element.attrib

        text = element.text
        tail = element.tail
        sub_elements = element.findall('*')
        if not self.minimize:
            record[ATTRIBUTES_KEY] = attributes
            record[TEXT_KEY] = text
            record[TAIL_KEY] = tail
            if sub_elements is not None:
                record[CHILDREN_KEY] = list(map(lambda elt: self.build(elt), sub_elements))
            else:
                record[CHILDREN_KEY] = None
        else:
            if len(attributes) > 0:
                record[ATTRIBUTES_KEY] = attributes
            if text is not None:
                text = text.strip()
                if len(text) > 0:
                    record[TEXT_KEY] = text
            if tail is not None:
                tail = tail.strip()
                if len(tail) > 0:
                    record[TAIL_KEY] = tail
            if sub_elements is not None and len(sub_elements) > 0:
                record[CHILDREN_KEY] = list(map(lambda elt: self.build(elt), sub_elements))
        return record


class XMLCrawler(Crawler):

    def __init__(self, source_name: str, source_file: str, default_offset: int = 0, source_encoding=None,
                 tag_selector=None, record_builder: XMLRecordBuilder = None):
        super().__init__(source_name, default_offset)
        self.source_file = source_file
        self.encoding = source_encoding
        self.tag_selector = tag_selector
        self.record_builder = DefaultXMLRecordBuilder() if record_builder is None else record_builder
        self._iterator = None

    def _get_records(self, offset: int = 0):
        tree = ElementTree.parse(self.source_file)
        self._iterator = tree.getroot().iter(tag=self.tag_selector)
        for i in range(offset):
            self.__next__()
        return self

    def __iter__(self):
        return self

    def __next__(self):
        element: Element = self._iterator.__next__()
        return self.record_builder.build(element)

    def _get_start_message(self):
        return f'Crawling {self.source_name} from {self.source_file} file.'
