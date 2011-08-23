class Mapping(dict):
    missing_elements = list
    def __getitem__(self, item):
        try:
            return super(Mapping, self).__getitem__(item)
        except KeyError:
            self[item] = self.missing_elements()
            return self[item]
