from abc import ABCMeta, abstractmethod


class MetaSerializer(metaclass=ABCMeta):

    @abstractmethod
    def dumps(self, obj):
        pass

    def dump(self, obj, file):
        pass

    def loads(self, string):
        pass

    def load(self, file):
        pass
