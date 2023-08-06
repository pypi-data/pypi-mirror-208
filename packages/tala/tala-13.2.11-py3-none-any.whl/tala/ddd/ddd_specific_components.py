from tala.utils.as_json import AsJSONMixin


class DDDSpecificComponents(AsJSONMixin):
    def __init__(self, ddd, parameter_retriever, parser):
        super(DDDSpecificComponents, self).__init__()
        self._ddd = ddd
        self._parameter_retriever = parameter_retriever
        self._parser = parser

    @property
    def parameter_retriever(self):
        return self._parameter_retriever

    @property
    def parser(self):
        return self._parser

    @property
    def ddd(self):
        return self._ddd

    @property
    def name(self):
        return self.ddd.name

    @property
    def ontology(self):
        return self.ddd.ontology

    @property
    def domain(self):
        return self.ddd.domain

    @property
    def service_interface(self):
        return self.ddd.service_interface

    @property
    def language_codes(self):
        return self.ddd.language_codes

    def reset(self):
        self.ontology.reset()
        if self.parser is not None:
            self.parser.clear()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, (self.ddd, self.parameter_retriever, self.parser))

    def as_dict(self):
        return self.ddd.as_dict()
