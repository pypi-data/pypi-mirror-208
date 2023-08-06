from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobClient, ContainerClient
from typing import Generic, TypeVar
from .serializers import ISerializer, JsonSerializer, JsonPickleSerializer

T = TypeVar('T')
    
class BlobStorage(Generic[T]):
    def __init__(self, connectionstring: str, container: str, serializer: ISerializer = JsonPickleSerializer()):
        self.connectionstring = connectionstring
        self.container = container
        self.serializer = serializer
        
    def get(self, key: str) -> None | T:
        '''Fetch a blob from the storage account. If the blob does not exist, None is returned. If a serializer is provided, the blob is deserialized before being returned.'''
        blob = BlobClient.from_connection_string(conn_str=self.connectionstring, container_name=self.container, blob_name=key)
        if blob.exists():
            content = blob.download_blob().readall()
            if self.serializer is None:
                return content
            return self.serializer.deserialize(content)
            
        return None
    
    def upsert(self, key: str, data: T) -> BlobClient:
        '''Upload a blob, overwriting any existing blob with the same key. If a serializer is provided, the data is serialized before being uploaded.'''
        container = ContainerClient.from_connection_string(conn_str=self.connectionstring, container_name=self.container)
        if container is None or not container.exists():
            container.create_container()
        
        serialized = data
        if self.serializer is not None:
            serialized = self.serializer.serialize(data)
        
        blob = container.get_blob_client(key)
        blob.upload_blob(serialized, overwrite=True)
        return blob
    
    def delete(self, key: str) -> None:
        '''Delete a blob from the storage account. If the blob does not exist, nothing happens (e.g. no exception is thrown).'''
        blob = BlobClient.from_connection_string(conn_str=self.connectionstring, container_name=self.container, blob_name=key)
        try:
            blob.delete_blob()
        except ResourceNotFoundError as e:
            # Do nothing, the blob does not exist, which is the state we wish to achieve by calling the delete method
            pass
        
    def exists(self, key: str) -> bool:
        '''Check if a blob exists in the container.'''
        blob = BlobClient.from_connection_string(conn_str=self.connectionstring, container_name=self.container, blob_name=key)
        return blob.exists()
    
class JsonBlobStorage(BlobStorage):
    def __init__(self, connectionstring: str, container: str):
        super().__init__(connectionstring, container, JsonSerializer())
        
class JsonPickleBlobStorage(BlobStorage):
    def __init__(self, connectionstring: str, container: str):
        super().__init__(connectionstring, container, JsonPickleSerializer())