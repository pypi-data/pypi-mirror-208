from dataclasses import dataclass
from bloboluni import BlobStorage, JsonBlobStorage, JsonPickleBlobStorage
import os, uuid
from dotenv import load_dotenv
load_dotenv()

@dataclass
class MyProfession:
    name: str
    description: str

@dataclass
class MyClass:
    name: str
    age: int
    profession: MyProfession
    
class SomeThingElse:
    def __init__(self, isCool, name) -> None:
        self.isCool = isCool
        self.name = name
        
    def amethod(self):
        return "A method"

if __name__ == "__main__":
    data = MyClass("blob", 30, MyProfession("Developer", "A developer"))

    connectionstring = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    storage = BlobStorage(connectionstring, "mycontainer")
    
    key = uuid.uuid4().hex
    blob = storage.get(key)
    assert blob is None
    storage.upsert(key, data)
    blob = storage.get(key)
    assert blob is not None
    print(type(blob))
    storage.delete(key)
    blob = storage.get(key)
    assert blob is None
    
    storage.upsert("something", SomeThingElse(True, "something"))
    
    somethingelse = storage.get("something")
    print(type(somethingelse))
    print(somethingelse)
    
    anotherthing = {"doDrugs": "cool"}
    storage.upsert("anotherthing", anotherthing)
    
    anotherthing = storage.get("anotherthing")
    print(type(anotherthing))
    print(anotherthing)
    
    
    