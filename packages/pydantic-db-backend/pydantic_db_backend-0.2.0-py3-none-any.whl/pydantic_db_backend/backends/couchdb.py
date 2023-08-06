from __future__ import annotations

import os
import sys
from typing import Dict, Type

import pydash
from pip._internal.metadata import Backend

import pydantic_db_backend.utils


class CouchDbBackend(Backend):
    _collections: Dict[Type[BaseModel], str] = {}
    _connections: Dict[str, CouchDbConnectionModel] = {}

    @classmethod
    def startup(cls, alias: str | None = "default", uri: str | None = None):
        super().startup()
        if uri is None:
            uri = os.environ.get('COUCHDB_URI', None)
            if uri is None:
                log.error("COUCHDB_URI not set.")
                sys.exit(-1)

        cls._connections[alias] = CouchDbConnectionModel(
            alias=alias,
            uri=uri,
            server=couchdb.Server(uri)
        )

    @classmethod
    def to_db(cls, instance: BackendModel) -> dict:
        document = super().to_db(instance)
        document = pydash.omit(document | {"_id": document['uid']}, "uid")
        return document

    @classmethod
    def from_db(cls, model: Type[BackendModel], document: dict) -> BackendModel:
        document = pydash.omit(document | {"uid": document['_id']}, "_id")
        return super().from_db(model, document)

    @classmethod
    def get_db(cls, db_name: str) -> couchdb.Database:
        with cls.alias() as alias:
            con = cls._connections[alias]
            if db_name in con.server:
                db = con.server[db_name]
            else:
                db = con.server.create(db_name)
        return db

    @classmethod
    def get_instance(cls, model: Type[BackendModel], uid: str) -> BackendModel:
        db = cls.get_db(db_name=cls.collection_name(model))
        return cls.from_db(model, db[uid])

    @classmethod
    def get_instance2(cls, model: Type[BackendModel], uid: str) -> BackendModel:
        db = cls.get_db(db_name=cls.collection_name(model))
        return cls.from_db(model, db[uid])

    @classmethod
    def post_document(cls, model: Type[BackendModel], document: dict) -> BackendModel:
        db = cls.get_db(db_name=cls.collection_name(model))
        db[document['_id']] = document

    @classmethod
    def post_instance(cls, instance: BackendModel) -> BackendModel:
        document = cls.to_db(instance)
        return cls.post_document(instance.__class__, document)

    @classmethod
    def put_instance(cls, instance: BackendModel) -> BackendModel:
        db = cls.get_db(db_name=cls.collection_name(instance.__class__))
        if pydantic_db_backend.utils.uid in db:
            record = db[pydantic_db_backend.utils.uid]
            record.update(cls.to_db(instance))
            db.save(record)
        else:
            return cls.post_instance(instance)


class CouchDbConnectionModel(BaseModel):
    alias: str
    uri: str
    server: couchdb.Server
    dbs: Dict[str, couchdb.Database] = Field(default_factory=dict)

    class Config():
        arbitrary_types_allowed = True
