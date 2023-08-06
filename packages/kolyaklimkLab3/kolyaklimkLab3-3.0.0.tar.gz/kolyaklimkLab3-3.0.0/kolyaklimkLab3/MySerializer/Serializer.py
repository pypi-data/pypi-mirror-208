from abc import ABC, abstractmethod


class Serializer(ABC):
    @abstractmethod
    def dumps(self, obj) -> str:
        pass

    @abstractmethod
    def loads(self, string: str):
        pass

    def dump(self, obj, path: str):
        with open(path, "w") as file:
            file.write(self.dumps(obj))

    def load(self, path):
        with open(path, "r") as file:
            return self.loads(file.read())
