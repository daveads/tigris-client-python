import json

import grpc

from api.generated.server.v1.api_pb2 import CreateOrUpdateCollectionRequest, CreateOrUpdateCollectionResponse, \
    DropCollectionRequest, DropCollectionResponse
from api.generated.server.v1.api_pb2_grpc import TigrisStub
from tigrisdb.collection import Collection
from tigrisdb.config import TigrisClientConfig
from tigrisdb.errors import TigrisException


class Database:
    __client: TigrisStub
    __config: TigrisClientConfig

    def __init__(self, client_stub: TigrisStub, config: TigrisClientConfig):
        self.__client = client_stub
        self.__config = config

    @property
    def project(self):
        return self.__config.project_name

    @property
    def branch(self):
        return self.__config.branch

    def create_or_update_collection(self, name: str, schema: dict) -> Collection:
        schema_str = json.dumps(schema)
        req = CreateOrUpdateCollectionRequest(
            project=self.project,
            branch=self.branch,
            collection=name,
            schema=schema_str.encode(),
            only_create=False
        )
        try:
            resp: CreateOrUpdateCollectionResponse = self.__client.CreateOrUpdateCollection(req)
            if resp.status == 'created':
                return Collection(name, self.__client, self.__config)
            else:
                raise TigrisException(f'failed to create collection: {resp.message}')
        except grpc.RpcError as e:
            raise TigrisException(f'failed to create collection: {e} ')

    def drop_collection(self, name: str) -> bool:
        req = DropCollectionRequest(
            project=self.project,
            branch=self.branch,
            collection=name,
        )

        try:
            resp: DropCollectionResponse = self.__client.DropCollection(req)
        except grpc.RpcError as e:
            raise TigrisException(f'failed to drop collection: {e} ')
        return resp.status == 'dropped'
