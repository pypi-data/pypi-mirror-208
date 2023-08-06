from abc import ABCMeta, abstractmethod


class MetaSerializer(metaclass=ABCMeta):

    @abstractmethod
    def dumps(self, obj):
        pass

    @abstractmethod
    def dump(self, obj, file):
        pass

    @abstractmethod
    def loads(self, string):
        pass

    @abstractmethod
    def load(self, file):
        pass
