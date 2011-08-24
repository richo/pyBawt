class Mapping(dict):
    def __getitem__(self, item):
        try:
            return super(Mapping, self).__getitem__(item)
        except KeyError:
            self[item] = []
            return self[item]

class LowerList(list):
    @staticmethod
    def lower(n):
        try:
            return n.lower()
        except AttributeError:
            return n
    def __contains__(self, value):
        return self.lower(value) in map(self.lower, self)
