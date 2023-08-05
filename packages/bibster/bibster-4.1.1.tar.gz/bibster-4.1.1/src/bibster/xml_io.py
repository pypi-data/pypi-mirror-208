import xml.etree.ElementTree as ET
import re, os


ESCAPE_RE = re.compile("(\")|(')|(<)|(>)|(&)|([\x00-\x1F])", re.UNICODE)
ESCAPE_COUNT = 6
ESCAPE_NAMES = ["quot", "apos", "lt", "gt", "amp"]

DEESCAPE_RE = re.compile("&([a-z]+);|&#([0-9]+);", re.UNICODE)
DEESCAPE_CHARACTERS = ["\"", "'", "<", ">", "&"]


def escape_xml_text(text):
    result = ""
    last_pos = 0
    pos = 0

    while True:

        match = ESCAPE_RE.search(text, pos=pos)

        if match is None:
            result += text[last_pos:]
            break

        pos = match.start(0)

        if pos > last_pos:
            result += text[last_pos:pos]

        for i in range(ESCAPE_COUNT):

            value = match.group(i + 1)

            if value is None:
                continue

            if i < ESCAPE_COUNT - 1:
                result += "&" + ESCAPE_NAMES[i] + ";"
            else:
                value = bytearray(value, "utf-8")[0]
                result += "&#{:d};".format(value)

            pos = match.end(0)
            last_pos = pos
            break

    return result


def deescape_xml_text(text):

    if text is None:
        text = ""

    result = ""
    last_pos = 0
    pos = 0

    while True:

        match = DEESCAPE_RE.search(text, pos=pos)

        if match is None:
            result += text[last_pos:]
            break

        pos = match.start(0)

        if pos > last_pos:
            result += text[last_pos:pos]

        value = match.group(1)

        if value is not None:

            value = value.lower()
            value_index = ESCAPE_NAMES.index(value)

            if value_index is None:
                result += value
            else:
                result += DEESCAPE_CHARACTERS[value_index]
        else:
            value = match.group(2)
            value = str(bytearray([int(value)]))

            result += value

        pos = match.end(0)
        last_pos = pos

    return result


def camelcase_to_snakecase(identifier):
    def handle_part(result, identifier, segment_start, segment_end):
        part = identifier[segment_start:segment_end]

        if part:
            if result and not (result.endswith("_") or part.startswith("_")):
                result += "_"
            result += part.lower()

        return result

    result = ""
    segment_start = 0

    for segment_end, c in enumerate(identifier):

        if c.isupper():
            result = handle_part(result, identifier, segment_start, segment_end)
            segment_start = segment_end

    result = handle_part(result, identifier, segment_start, len(identifier))

    return result


def apply_linebreak(some_text, linebreak):

    lines = []
    pos = 0
    should_append_empty_line = True

    while pos < len(some_text):
        index = some_text.find(linebreak, pos)

        if index < 0:
            lines.append(some_text[pos:])
            should_append_empty_line = False
            break

        lines.append(some_text[pos:index])
        pos = index + len(linebreak)

    if (lines and should_append_empty_line) or not lines:
        lines.append("")

    return lines


def apply_linebreaks(some_text, linebreaks):

    lines = [some_text]
    next_lines = []

    for linebreak in linebreaks:

        for line in lines:
            nested_lines = apply_linebreak(line, linebreak)
            next_lines.extend(nested_lines)

        lines = next_lines
        next_lines = []

    return lines


class XMLFormat(object):

    @property
    def indent_string(self):
        if self.indent_string_ is None:
            self.indent_string_ = " " * (self.indent_level_ * self.indent_spacing_)

        return self.indent_string_

    @property
    def indent_level(self):
        return self.indent_level_

    @indent_level.setter
    def indent_level(self, value):
        if value != self.indent_level_:
            self.indent_level_ = value
            self.indent_string_ = None

    @property
    def indent_spacing(self):
        return self.indent_spacing_

    @indent_spacing.setter
    def indent_spacing(self, value):
        if value != self.indent_spacing_:
            self.indent_spacing_ = value
            self.indent_string_ = None

    class LevelManager(object):

        def __init__(self, output, level):
            self.output_ = output
            self.saved_level_ = level

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.output_.indent_level = self.saved_level_

    def __init__(self):
        self.indent_level_ = 0
        self.indent_spacing_ = 2
        self.indent_string_ = None
        self.linebreak_ = os.linesep

    def __call__(self, some_text, initial_line_break=True):
        lines = apply_linebreaks(some_text, linebreaks=["\r\n", "\n", "\r"])
        lines = [self.indent_string + line for line in lines]
        result = self.linebreak_.join(lines)
        if initial_line_break:
            result = self.linebreak_ + result
        return result

    def relative_indent_scope(self, indent_delta):
        manager = self.LevelManager(self, self.indent_level)
        self.indent_level += indent_delta
        return manager

    def absolute_indent_scope(self, indent_value):
        manager = self.LevelManager(self, self.indent_level)
        self.indent_level += indent_value
        return manager


class XMLBase(object):

    def get_xml_keyword_assignments(self):
        return []

    def get_xml_name(self):
        return ""

    def set_xml_name(self, name):
        pass


def find_xml_root_class(object):
    visited_classes = set()
    candidates = [(object.__class__, object.__class__.__bases__)]

    while candidates:

        base_class, classes = candidates[0]
        candidates.pop(0)

        visited_classes.add(base_class)

        for cls in classes:
            if cls is XMLBase:
                return base_class

            if cls not in visited_classes:
                candidates.append((cls, cls.__bases__))

    return None


def xml_attributes_old(instance):

    root_class = find_xml_root_class(instance)

    if root_class:
        super_attributes = set()
        for base in root_class.__bases__:
            super_attributes |= set(dir(base()))
    else:
        super_attributes = set(dir(object()))

    attributes = set(instance.__dir__()) - super_attributes

    for attribute in list(attributes):

        if attribute.startswith("__") and attribute.endswith("__"):
            attributes.remove(attribute)
            continue

        if attribute.startswith("_") or attribute.endswith("_"):
            attributes.remove(attribute)
            continue

    return sorted(attributes), root_class is not None


def xml_keyword_assignments(instance):

    if not isinstance(instance, XMLBase):
        return False, []

    xml_keyword_assignments = instance.get_xml_keyword_assignments()
    return True, xml_keyword_assignments


class XMLReference(object):

    def __init__(self, object_id):
        self.object_id = object_id

    def format_element(self):
        return "<reference>{:d}</reference>".format(self.object_id)

    @staticmethod
    def from_element(element):

        try:
            value = int(element.text)
        except ValueError:
            raise XMLInflationError("Couldn't convert \"\" to reference id.".format(element.text))

        return XMLReference(value)


class XMLValue(object):

    def format_element(self):
        return ""


class IntegerValue(XMLValue):

    def __init__(self, value):
        self.value = value

    def format_element(self):
        return "<integer>{:d}</integer>".format(self.value)

    @staticmethod
    def from_element(element):

        try:
            value = int(element.text)
        except ValueError:
            raise XMLInflationError("Couldn't convert \"\" to integer.".format(element.text))

        return IntegerValue(value)


class RealValue(XMLValue):

    def __init__(self, value):
        self.value = value

    def format_element(self):
        return "<real>{:f}</float>".format(self.value)

    @staticmethod
    def from_element(element):

        try:
            value = float(element.text)
        except ValueError:
            raise XMLInflationError("Couldn't convert \"\" to real.".format(element.text))

        return RealValue(value)


class StringValue(XMLValue):

    def __init__(self, value):
        self.value = value

    def format_element(self):
        value = escape_xml_text(self.value)
        if not value:
            return "<string/>"
        return "<string>{}</string>".format(value)

    @staticmethod
    def from_element(element):

        try:
            value = deescape_xml_text(element.text)
        except ValueError:
            raise XMLInflationError("Couldn't convert \"\" to string.".format(element.text))

        return StringValue(value)


class NoneValue(XMLValue):

    value = None

    def format_element(self):
        return "<none/>"

    @staticmethod
    def from_element(element):

        if element.text:
            raise XMLInflationError("\"\" cannot represent a none value.".format(element.text))

        return NoneValue()


class ArrayValue(XMLValue):

    def __init__(self, value):
        self.value = value

    def format_element(self):

        format = XMLFormat()

        xml_text = format("<array>", initial_line_break=False)

        for array_element in self.value:

            with format.relative_indent_scope(1):
                xml_text += format("<value>" + array_element.format_element() + "</value>")

        xml_text += format("</array>")
        return xml_text

    @staticmethod
    def from_element(element, object_references):

        inflated_values = []
        result = ArrayValue(inflated_values)

        for index, value in enumerate(element):

            value = list(value)

            if len(value) != 1:
                raise XMLInflationError("Expecting exactly one child element in <value>.")

            value = value[0]

            if value.tag == "reference":
                value = XMLReference.from_element(value)
                object_references.append((value, inflated_values, index))
            else:
                is_value, xml_value = xml_value_from_element(value, object_references)

                if not is_value:
                    raise XMLInflationError("<array> element contains invalid value: \"{}\".".format(value.text))

                value = xml_value.value

            inflated_values.append(value)

        return result


class DictionaryValue(XMLValue):

    def __init__(self, value):
        self.value = value

    def format_element(self):

        format = XMLFormat()

        xml_text = format("<dict>", initial_line_break=False)

        keys = sorted(self.value.keys(), key=lambda x: x.value)

        for key in keys:

            value =self.value[key]

            with format.relative_indent_scope(1):
                xml_text += format("<item>")

                with format.relative_indent_scope(1):
                    xml_text += format("<key>" + key.format_element() + "</key>")

                with format.relative_indent_scope(1):
                    xml_text += format("<value>" + value.format_element() + "</value>")

                xml_text += format("</item>")

        xml_text += format("</dict>")
        return xml_text

    @staticmethod
    def from_element(element, object_references):

        inflated_values = {}
        result = DictionaryValue(inflated_values)

        for item in element:

            if item.tag != "item":
                raise XMLInflationError("Unexpected <{}> element in <dict>.".format(item.tag))

            key = item.findall("key")

            if len(key) != 1:
                raise XMLInflationError("Expecting exactly one <key> element in <item>.")

            key = key[0]
            key = list(key)

            if len(key) != 1:
                raise XMLInflationError("Expecting exactly one child element in <key>.")

            key = key[0]

            is_value, key = xml_value_from_element(key, object_references)

            if not is_value:
                raise XMLInflationError("<key> element contains invalid value: \"{}\".".format(key.text))

            key = key.value

            value = item.findall("value")

            if len(value) != 1:
                raise XMLInflationError("Expecting exactly one <value> element in <item>.")

            value = value[0]
            value = list(value)

            if len(value) != 1:
                raise XMLInflationError("Expecting exactly one child element in <value>.")

            value = value[0]

            if value.tag == "reference":
                value = XMLReference.from_element(value)
                object_references.append((value, inflated_values, key))
            else:
                is_value, xml_value = xml_value_from_element(value, object_references)

                if not is_value:
                    raise XMLInflationError("<array> element contains invalid value: \"{}\".".format(value.text))

                value = xml_value.value

            inflated_values[key] = value

        return result


def flatten_nested_xml_object(value, xml_list, visited):

    nested_object_id = visited.get(value, len(visited) + 1)
    nested_keyword_assignments = []

    if nested_object_id > len(visited):
        is_nested_xml_object, nested_keyword_assignments = xml_keyword_assignments(value)
    else:
        is_nested_xml_object = False

    result = XMLReference(nested_object_id) if is_nested_xml_object else NoneValue()

    if nested_object_id <= len(visited):
        return result

    visited[value] = nested_object_id

    xml_list.append((nested_object_id, value, nested_keyword_assignments))
    return result


def flatten_xml_value(value, xml_list, visited):

    if value is None:
        return True, NoneValue()

    if isinstance(value, int):
        return True, IntegerValue(value)

    if isinstance(value, float):
        return True, RealValue(value)

    if isinstance(value, str):
        return True, StringValue(value)

    if isinstance(value, list) or isinstance(value, tuple):

        flat_list = []

        for element in value:
            flat_list.append(flatten_any_for_xml(element, xml_list, visited))

        return True, ArrayValue(flat_list)

    if isinstance(value, dict):

        flat_dict = {}

        for key, value in value.items():

            is_key_flat, flat_key = flatten_xml_value(key, xml_list, visited)

            if not is_key_flat:
                raise XMLDeflationError("Couldn't flatten dictionary key of type \"{}\".".format(type(key).name))

            flat_value = flatten_any_for_xml(value, xml_list, visited)

            flat_dict[flat_key] = flat_value

        return True, DictionaryValue(flat_dict)

    return False, value


def flatten_any_for_xml(value, xml_list, visited):

    is_xml_value, value = flatten_xml_value(value, xml_list, visited)

    if is_xml_value:
        return value

    return flatten_nested_xml_object(value, xml_list, visited)


def flatten_object_for_xml(instance):

    is_nested_xml_object, keyword_assignments = xml_keyword_assignments(instance)

    if not is_nested_xml_object:
        return None

    visited = {instance: 1}
    xml_list = [(1, instance, keyword_assignments)]
    index = 0

    while index < len(xml_list):

        object_id, instance, keyword_assignments = xml_list[index]

        keyword_assignments = [(assignment[0], flatten_any_for_xml(assignment[1], xml_list, visited)) \
                               for assignment in keyword_assignments]

        xml_list[index] = object_id, instance, keyword_assignments
        index += 1

    return xml_list


def deflate_object_to_xml(instance):

    xml_list = flatten_object_for_xml(instance)

    if xml_list is None:
        return ""


    format = XMLFormat()

    xml_text = format("<?xml version=\"1.0\" encoding=\"utf-8\"?>", initial_line_break=False)
    xml_text += format("<style>")

    for object_id, instance, element_keyword_assignments in xml_list:

        object_name = camelcase_to_snakecase(instance.__class__.__name__)
        xml_name = instance.get_xml_name()

        with format.relative_indent_scope(1):
            xml_text += format("<{} id=\"{:d}\"{}>".format(object_name, object_id, " name=\"{}\"".format(xml_name) if xml_name else ""))

            with format.relative_indent_scope(1):

                for attribute, value in element_keyword_assignments:

                    xml_text += format("<attribute name=\"{}\">".format(escape_xml_text(attribute)))

                    with format.relative_indent_scope(1):
                        xml_text += format("<value>" + value.format_element() + "</value>")

                    xml_text += format("</attribute>")

            xml_text += format("</{}>".format(object_name))

    xml_text += format("</style>")
    return xml_text


class XMLDeflationError(RuntimeError):
    pass


class XMLInflationError(RuntimeError):
    pass


XML_VALUE_ELEMENT_REGISTRY = {

    "none": lambda x, object_references: NoneValue.from_element(x),
    "integer": lambda x, object_references: IntegerValue.from_element(x),
    "real": lambda x, object_references: RealValue.from_element(x),
    "string": lambda x, object_references: StringValue.from_element(x),
    "array": lambda x, object_references: ArrayValue.from_element(x, object_references),
    "dict": lambda x, object_references: DictionaryValue.from_element(x, object_references)

}


def xml_value_from_element(element, object_references):

    converter = XML_VALUE_ELEMENT_REGISTRY.get(element.tag, None)

    if converter is None:
        return False, None

    return True, converter(element, object_references)


def xml_object_from_element(element, object_references):

    element_id = element.get("id", None)

    if element_id is None:
        raise XMLInflationError("<\"{}\"> element is missing required id attribute.".format(element.tag))

    try:
        element_id = int(element_id)
    except ValueError:
        raise XMLInflationError(
            "<\"{}\"> element has invalid id attribute: \"{}\".".format(element.tag, str(element_id)))

    element_name = element.get("name", "")

    element_keyword_assignments = []

    for attribute in element.findall("attribute"):

        attribute_name = attribute.get("name", None)

        if attribute_name is None:
            raise XMLInflationError("<attribute> element is missing required name attribute.")

        attribute_name = deescape_xml_text(attribute_name)
        attribute_value = attribute.findall("value")

        if len(attribute_value) != 1:
            raise XMLInflationError("An <attribute> element is expected to contain exactly one <value> element.")

        attribute_value = attribute_value[0]
        attribute_value = list(attribute_value)

        if len(attribute_value) != 1:
            raise XMLInflationError(
                "An <value> element is expected to contain exactly one child element representing its value.")

        attribute_value = attribute_value[0]

        if attribute_value.tag == "reference":
            attribute_value = XMLReference.from_element(attribute_value)
        else:
            is_value, attribute_value = xml_value_from_element(attribute_value, object_references)

            if not is_value:
                raise XMLInflationError("<value> element contains child which cannot be interpreted as a value: \"{}\".".format(attribute_value.text))

        element_keyword_assignments.append((attribute_name, attribute_value))

    return element_id, element_name, element_keyword_assignments


def inflate_object_from_xml(xml_text, element_registry):

    xml_tree = ET.fromstring(xml_text)

    root_object_id = None

    object_registry = {}
    object_references = []

    style_element = xml_tree

    for element in style_element:

        element_class = element_registry.get(element.tag, None)

        if element_class is None:
            raise XMLInflationError("Unknown style element type: <\"{}\">.".format(element.tag))

        reference_base = len(object_references)
        element_id, element_name, element_keyword_assignments = xml_object_from_element(element, object_references)
        element_dependencies = []

        for i in range(reference_base, len(object_references)):
            element_dependencies.append(object_references[i][0].object_id)

        object_registry[element_id] = element_class, element_name, element_keyword_assignments

        if root_object_id is None:
            root_object_id = element_id

    # collate and sort object ids
    object_ids = sorted(object_registry.keys())

    # instantiate objects *without* initialising them
    for object_id in object_ids:

        element_class, element_name, element_keyword_assignments = object_registry[object_id]
        instance = element_class.__new__(element_class)
        object_registry[object_id] = instance, element_name, element_keyword_assignments

    # replace object references in nested data values

    for reference, host, attribute in object_references:

        if reference.object_id not in object_registry:
            raise XMLInflationError("Unresolvable object id: {:d}.".format(reference.object_id))

        instance, _, _ = object_registry[reference.object_id]
        host[attribute] = instance


    # resolve argument and keyword values for objects

    for object_id in object_ids:

        instance, element_name, element_keyword_assignments = object_registry[object_id]

        keywords = {}

        for attribute, value in element_keyword_assignments:

            if isinstance(value, XMLReference):

                if value.object_id not in object_registry:
                    raise XMLInflationError("Unresolvable object id: {:d}.".format(value.object_id))

                value, _, _ = object_registry[value.object_id]

            else:
                value = value.value

            keywords[attribute] = value

        instance.__class__.__init__(instance, **keywords)
        instance.set_xml_name(element_name)

    instance, _, _ = object_registry[root_object_id]

    return instance


import inspect


def xml_capture_caller_arguments():

    frame = inspect.currentframe()

    if frame is None:
        return None

    frame = frame.f_back

    if frame is None:
        return None

    args, _, _, values = inspect.getargvalues(frame)

    values.pop("self", None)
    values.pop("__class__", None)

    return list(values.items())