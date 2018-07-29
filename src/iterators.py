class Iterator(object):
    def __init__(self, source):
        if isinstance(source, list):
            self.source = iter(source).__iter__()

    def __iter__(self):
        return self

    def next(self):
        return self.source.next()


class TestCase(object):
    def test_iter(self):
        iterator = Iterator([1, 2, 3])

        assert [1, 2, 3] == [n for n in iterator]