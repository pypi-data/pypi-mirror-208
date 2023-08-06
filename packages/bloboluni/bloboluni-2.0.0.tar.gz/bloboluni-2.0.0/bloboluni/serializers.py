import abc
from typing import Generic, TypeVar
import json
from json import JSONEncoder
import jsonpickle

T = TypeVar('T')

class ISerializer(Generic[T]):
    @abc.abstractmethod
    def serialize(self, data: T) -> str:
        pass
    
    @abc.abstractmethod
    def deserialize(self, data: str) -> T:
        pass
    
class BlobJsonEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
    
class JsonSerializer(ISerializer[T]):
    def serialize(self, data: T) -> str:
        return BlobJsonEncoder().encode(data)
    
    def deserialize(self, data: str) -> T:
        return json.loads(data)

class JsonPickleSerializer(ISerializer[T]):
    def serialize(self, data: T) -> str:
        return jsonpickle.encode(data)
    
    def deserialize(self, data: str) -> T:
        return jsonpickle.decode(data)