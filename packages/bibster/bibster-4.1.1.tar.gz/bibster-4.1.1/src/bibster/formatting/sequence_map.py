from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa

from ..xml_io import XMLBase, xml_capture_caller_arguments

__all__ = ['SequenceMap']


class SequenceMap(XMLBase):

    """Represents a repeating pattern of values."""

    def __init__(self,
                 congruence_assignments: Iterable[Tuple[int, Any]],
                 default_assignment: Any,
                 period: int = 0,
                 absolute_assignments: Iterable[Tuple[int, Any]] = None):

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        assignment_by_congruence = {}

        for rank, value in congruence_assignments:

            if period is not None and period > 0 and (rank >= period or -rank > period):
                continue

            assignment_by_congruence[rank] = value

        if absolute_assignments is None:
            absolute_assignments = tuple()

        assignment_by_index = {}

        for index, value in absolute_assignments:
            assignment_by_index[index] = value

        self.period_ = period
        self.assignment_by_congruence_ = assignment_by_congruence
        self.assignment_by_index_ = assignment_by_index
        self.default_assignment_ = default_assignment
        self.xml_name_ = ""

    def lookup(self, index, n=None):

        p = self.period_

        if not p:
            p = n

        congruence_index = index % p

        value = self.assignment_by_congruence_[congruence_index] if congruence_index in self.assignment_by_congruence_ \
            else self.assignment_by_congruence_.get(congruence_index - p, self.default_assignment_)

        value = self.assignment_by_index_.get(index, value)

        return value

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name

    def __hash__(self):
        return hash((self.period_, tuple(self.assignment_by_congruence_.items()),
                     tuple(self.assignment_by_index_.items()), self.default_assignment_))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, SequenceMap):
            return False

        return self.period_ == other.period_ and \
            self.assignment_by_congruence_ == other.assignment_by_congruence_ and \
            self.assignment_by_index_ == other.assignment_by_index_ and \
            self.default_assignment_ == other.default_assignment_

    def __ne__(self, other):
        return not self.__eq__(other)
