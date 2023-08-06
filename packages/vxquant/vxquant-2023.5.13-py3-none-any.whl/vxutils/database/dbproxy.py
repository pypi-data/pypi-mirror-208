"""monogodb wrapper"""

import pymongo
import contextlib
from vxutils.convertors import local_tzinfo
from vxutils import vxDict, logger, retry

if pymongo.version_tuple[0] <= 4:
    Warning(f"当前pymongo版本为 {pymongo.version} ，推荐升级至 4.0以上。")


try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
except ImportError:
    MongoClient = None
    if pymongo.version_tuple[0] <= 4:
        raise ImportError(f"当前pymongo版本为 {pymongo.version} ，推荐升级至 4.0以上。")

try:
    from pymongo import Connection
except ImportError:
    Connection = None

try:
    from pymongo import ReplicaSetConnection
except ImportError:
    ReplicaSetConnection = None


def get_methods(*objs):
    return {
        attr
        for obj in objs
        for attr in dir(obj)
        if not attr.startswith("_") and hasattr(getattr(obj, attr), "__call__")
    }


EXECUTABLE_MONGO_METHODS = get_methods(
    pymongo.collection.Collection,
    pymongo.database.Database,
    MongoClient,
    pymongo,
)


def get_connection(obj):
    if isinstance(obj, Collection):
        return obj.database.connection
    elif isinstance(obj, Database):
        return obj.connection
    elif isinstance(obj, MongoClient):
        return obj
    else:
        return None


def get_client(obj):
    if isinstance(obj, MongoClient):
        client = obj
    elif isinstance(obj, Database):
        client = obj.client
    elif isinstance(obj, Collection):
        client = obj.database.client
    else:
        client = None
    return client


def is_replica_set(obj):
    try:
        get_client(obj)["admin"].command("command", "replSetGetStatus")
        return True
    except pymongo.errors.OperationFailure:
        return False


class vxMongoProxy(object):
    """Proxy for MongoDB connection.
    Methods: i.e find, insert etc, 自动处理autoreconnect 错误.
    """

    def __init__(self, conn):
        """conn is an ordinary MongoDB-connection."""
        self.conn = conn
        self._deco_retry = retry(5, (pymongo.errors.AutoReconnect,))

    @property
    def db_connection(self):
        return get_connection(self.conn)

    @property
    def mongo_client(self):
        return get_client(self.conn)

    def __getitem__(self, key):
        """Create and return proxy around the method in the connection
        named "key".
        """
        item = self.conn[key]
        return vxMongoProxy(item) if hasattr(item, "__call__") else item

    def __getattr__(self, key):
        """If key is the name of an executable method in the MongoDB connection,
        for instance find or insert, wrap this method in Executable-class that
        handles AutoReconnect-Exception.
        """
        attr = getattr(self.conn, key)
        if hasattr(attr, "__call__"):
            if key in EXECUTABLE_MONGO_METHODS:
                return self._deco_retry(attr)
            else:
                return vxMongoProxy(attr)
        return attr

    def __call__(self, *args, **kwargs):
        return self.conn(*args, **kwargs)

    def __dir__(self):
        return dir(self.conn)

    def __str__(self):
        return self.conn.__str__()

    def __repr__(self):
        return self.conn.__repr__()

    def __nonzero__(self):
        return True

    @classmethod
    def connect(cls, db_uri: str, db_name: str = None):
        db_conn = MongoClient(
            db_uri, document_class=vxDict, tz_aware=True, tzinfo=local_tzinfo
        )

        return cls(db_conn.get_database(db_name)) if db_name else cls(db_conn)

    @contextlib.contextmanager
    def start_session(
        self,
        causal_consistency=None,
        default_transaction_options=None,
        snapshot=None,
        lock=None,
    ):
        if lock:
            lock.acquire()
        try:
            with self.mongo_client.start_session(
                causal_consistency, default_transaction_options, snapshot
            ) as session:
                if is_replica_set(self.conn):
                    with session.start_transaction():
                        yield session
                else:
                    yield session
        finally:
            if lock:
                lock.release()


if __name__ == "__main__":
    # db.createUser({user: "writer", pwd: "vxquant202#", roles: ["readWrite"]})
    a = vxMongoProxy.connect(
        "mongodb://writer:vxquant202#@127.0.0.1:27017/quant", "quant"
    )
    cur = a["accounts"].find_one_and_update(
        {"a": 1}, {"$set": {"a": 1, "b": 2}}, multi=True
    )
    # print(cur.inserted_id)

    with a.start_session() as session:
        a["accounts"].find({})

    cur = a["accounts"].find({})
    for item in cur:
        print(item)
