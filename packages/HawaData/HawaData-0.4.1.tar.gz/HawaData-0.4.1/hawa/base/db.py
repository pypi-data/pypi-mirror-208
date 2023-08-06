import MySQLdb
import mongoengine
import sqlalchemy
from redis.client import StrictRedis

from hawa.base.decos import singleton
from hawa.config import project

metadata = sqlalchemy.MetaData()


@singleton
class DbUtil:
    _conn = None
    _cursor_conn = None
    _engine_conn = None

    @property
    def conn(self):
        """engine wrapper for pandas.read_sql"""
        if project.COMPLETED:
            try:
                if not self._conn:
                    self._conn = self.db_engine
                return self._conn
            except Exception as e:
                project.logger.info(f"{type(e)=} {e=}")
                self._conn = self.db_engine
                return self._conn
        return self.db_engine

    @property
    def engine_conn(self):
        if not self._engine_conn:
            self._engine_conn = self.db_engine.connect()
        return self._engine_conn

    @property
    def db_engine(self):
        database_url = f"{project.DB_MODE}://{project.DB_USER}:{project.DB_PSWD}@{project.DB_HOST}/" \
                       f"{project.DB_NAME}?charset=utf8"
        engine = sqlalchemy.create_engine(database_url)
        return engine

    def connect(self):
        return MySQLdb.connect(
            host=project.DB_HOST,
            port=project.DB_PORT,
            user=project.DB_USER,
            passwd=project.DB_PSWD,
            db=project.DB_NAME,
        )

    @property
    def cursor(self):
        """only for test"""
        return self.cursor_conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    @property
    def cursor_conn(self):
        if not self._cursor_conn:
            self._cursor_conn = self.connect()
        if not self._cursor_conn.open:
            self._cursor_conn = self.connect()
        # is self._cursor_conn alive?
        try:
            self._cursor_conn.ping()
        except Exception as e:
            project.logger.info(f"{type(e)=} {e=}")
            self._cursor_conn = self.connect()
        return self._cursor_conn

    def query_by_sql(self, sql: str, mode: str = 'all'):
        """
        :param sql:
        :param mode: all or one
        :return: list or dict by mode
        """
        with self.cursor_conn.cursor(cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            match mode:
                case 'all':
                    return cursor.fetchall()
                case 'one':
                    return cursor.fetchone()


class MongoUtil:
    @classmethod
    def connect(self):
        mongoengine.connect(
            project.MONGO_DB,
            host=project.MONGO_HOST, port=project.MONGO_PORT,
            username=project.MONGO_USER,
            password=project.MONGO_PSWD,
            authentication_source=project.MONGO_AUTH_DB
        )


@singleton
class RedisUtil:
    @property
    def conn(self):
        return StrictRedis(
            host=project.REDIS_HOST,
            db=project.REDIS_DB,
            decode_responses=True,
        )
