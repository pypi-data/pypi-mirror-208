from .base import MarkupMetadata

__all__ = ['SequenceEllipsis', 'EndEllipsis', 'FixedEllipsis']


class SequenceEllipsis(object):

    def __call__(self, elements_and_separators):
        return elements_and_separators


class EndEllipsis(SequenceEllipsis):

    def __init__(self, limit=3, replacement="..."):
        super().__init__()
        self.limit_ = limit
        self.replacement_ = replacement

    def __call__(self, elements_and_separators):

        n_elements = (len(elements_and_separators) - 1) // 2

        if n_elements <= self.limit_:
            return elements_and_separators

        result = elements_and_separators[:self.limit_ * 2] + \
            [(self.replacement_, MarkupMetadata()), elements_and_separators[-1]]
        return result


class FixedEllipsis(SequenceEllipsis):

    def __init__(self, index=1, limit=3, replacement="..."):
        super().__init__()
        self.index_ = index
        self.limit_ = limit
        self.replacement_ = replacement

    def __call__(self, elements_and_separators):

        n_elements = (len(elements_and_separators) - 1) // 2

        if n_elements <= self.limit_:
            return elements_and_separators

        result = elements_and_separators[:self.index_ * 2] + \
            [(self.replacement_, MarkupMetadata()), elements_and_separators[-1]]
        return result
