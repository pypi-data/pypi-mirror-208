# -*- coding: utf-8 -*-

import csv
import datetime
import json
from xml.etree.ElementTree import ElementTree, Element, SubElement, indent as xml_indent

from monkey.crawler.op_codes import OpCode

from monkey.crawler.processor import Processor, ProcessingError


class DumpProcessor(Processor):
    def __init__(self, file_path: str, encoding='utf-8', newline='', name: str = None):
        """
        Instantiates the processor
        :param file_path: the path of dump file
        :param encoding: the encoding to use
        :param newline: the newline marker
        :param name: The friendly name of the processor
        """
        super().__init__(name)
        self.file_path = file_path
        self.encoding = encoding
        self.newline = newline
        self.output_file = None

    def _enter(self):
        self.output_file = open(self.file_path, 'w', encoding=self.encoding, newline=self.newline)

    def _exit(self):
        self.output_file.close()


class DummyDumpProcessor(DumpProcessor):
    """A simple processor that dumps records into a text file, using the standard to string conversion."""

    def __init__(self, file_path: str, encoding='utf-8', newline='\n', name: str = None):
        """
        Instantiates the processor
        :param file_path: the path of dump file
        :param encoding: the encoding to use
        :param newline: the newline marker
        :param name: The friendly name of the processor
        """
        super().__init__(file_path, encoding, newline, name)

    def _process(self, record):
        self.output_file.write(str(record) + self.newline)
        return OpCode.SUCCESS


class CSVDumpProcessor(DumpProcessor):
    """A processor that dumps records into a CSV file."""

    def __init__(self, file_path: str, encoding: str = 'utf-8', newline: str = '', col_heads: list[str] = None,
                 restval: str = '', extrasaction: str = 'raise', dialect: str = 'excel', name: str = None):
        """
        Instantiates the processor
        :param file_path: the path of dump file
        :param encoding: the encoding to use
        :param newline: the newline marker
        :param col_heads: the heading of columns
        :param restval:
        :param extrasaction:
        :param dialect:
        :param name: The friendly name of the processor
        """
        super().__init__(file_path, encoding, newline, name)
        self.col_heads = col_heads
        self.restval = restval
        self.extrasaction = extrasaction
        self.dialect = dialect

    def _enter(self):
        super()._enter()
        self.writer = csv.DictWriter(self.output_file, self.col_heads, restval=self.restval,
                                     extrasaction=self.extrasaction, dialect=self.dialect)
        self.writer.writeheader()

    def _exit(self):
        super()._exit()

    def _process(self, record):
        self.writer.writerow(record)
        return OpCode.SUCCESS


class JSONDumpProcessor(DumpProcessor):
    """A processor that dumps records into a JSON file."""

    def __init__(self, file_path: str, encoding='utf-8', newline='', encoder: json.JSONEncoder = None,
                 top_element_name: str = None, name: str = None):
        """
        Instantiates the processor
        :param file_path: the path of dump file
        :param encoding: the encoding to use
        :param newline: the newline marker
        :param encoder:
        :param top_element_name:
        :param name: The friendly name of the processor
        """
        super().__init__(file_path, encoding, newline, name)
        self.encoder = JSONEncoder() if encoder is None else encoder
        self.top_element_name = self.name if top_element_name is None else top_element_name
        self.sep = ''

    def _enter(self):
        super()._enter()
        self.output_file.write(f'{{"{self.top_element_name}":[')

    def _exit(self):
        self.output_file.write(']}')
        self.sep = ''
        super()._exit()

    def _process(self, record):
        self.output_file.write(f'{self.sep}{self.encoder.encode(record)}')
        self.sep = ','
        return OpCode.SUCCESS


class XMLElementBuilder:

    def build(self, parent_elt, elt_name: str, record) -> OpCode:
        """Instantiates the XML content structure representing the record
        :param parent_elt: The parent element of the new element to create
        :param elt_name: the name of element to create
        :param record: The record object to process
        :return: The executed operation code
        """
        elt = SubElement(parent_elt, elt_name)
        return self._build(elt, record)

    def _build(self, elt, record) -> OpCode:
        """Builds the XML content structure representing the record
        :param elt: the element representing the record
        :param record: The record object to process
        :return: The executed operation code
        """
        raise NotImplemented()


class DefaultXMLElementBuilder(XMLElementBuilder):

    def _build(self, elt, record) -> OpCode:
        """Builds the XML content structure representing the record
        :param elt: the element representing the record
        :param record: The record object to process
        :return: The executed operation code
        """
        try:
            for key, value in record.items():
                sub_elt = SubElement(elt, str(key).replace(' ', '_').lower())
                if isinstance(value, dict):
                    self._build(sub_elt, value)
                if isinstance(value, datetime.datetime):
                    sub_elt.text = value.isoformat()
                else:
                    sub_elt.text = value
            return OpCode.SUCCESS
        except Exception:
            raise ProcessingError(record, 'Failed to build XML representation', e)


class XMLDumpProcessor(DumpProcessor):
    """A processor that dumps records into an XML file."""

    def __init__(self, file_path: str, element_builder: XMLElementBuilder, encoding='utf-8',
                 root_element_name: str = 'root', record_element_name: str = 'record', xml_declaration=None,
                 pretty=False, name: str = None):
        super().__init__(file_path, encoding, '', name)
        self.element_builder = element_builder
        self.root_element_name = self.name if root_element_name is None else root_element_name
        self.record_element_name = self.name if record_element_name is None else record_element_name
        self.xml_declaration = xml_declaration
        self.pretty = pretty
        self._element_tree = None

    def _enter(self):
        root = Element(self.root_element_name)
        self._element_tree = ElementTree(root)

    def _exit(self):
        if self.pretty:
            xml_indent(self._element_tree)
        self._element_tree.write(self.file_path, encoding=self.encoding, xml_declaration=self.xml_declaration)
        self._element_tree = None

    def _process(self, record):
        """Actual processing of a handled objet
        :param record: The record object to process
        :return: The executed operation code
        """
        return self.element_builder.build(self._element_tree.getroot(), self.record_element_name, record)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)
