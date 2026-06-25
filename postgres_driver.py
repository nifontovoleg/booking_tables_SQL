import os
from dotenv import load_dotenv
import psycopg2
import inspect
from datetime import datetime
from typing import get_type_hints, Optional, get_origin, get_args, Union


class PostgresDriver:
    TYPE_MAP = {
        int: "INT",
        str: "TEXT",
        bool: "BOOLEAN",
        float: "NUMERIC(10,2)",
        datetime: "TIMESTAMP",
    }

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        load_dotenv()
        self.dbname = dbname or os.getenv("DB_NAME")
        self.user = user or os.getenv("DB_USER")
        self.password = password or os.getenv("DB_PASSWORD")
        self.host = host or os.getenv("DB_HOST")
        self.port = port or os.getenv("DB_PORT")

        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.conn.autocommit = False

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def _python_type_to_postgres(self, python_type) -> str:
        origin = get_origin(python_type)

        if origin is Union and type(None) in get_args(python_type):
            inner = next(t for t in get_args(python_type) if t is not type(None))
            return self._python_type_to_postgres(inner)

        return self.TYPE_MAP.get(python_type, self.TYPE_MAP.get(origin, "TEXT"))

    def _check_table_exists(self, table_name: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """, (table_name,))
            return cur.fetchone()[0]

    def _generate_create_table_sql(self, model_class, table_name: str) -> str:
        type_hints = get_type_hints(model_class)
        annotations = getattr(model_class, "__annotations__", {})
        col_defs = []

        for name in annotations:
            if name.startswith("_"):
                continue
            value = getattr(model_class, name, None)
            if inspect.ismethod(value) or inspect.isfunction(value):
                continue

            python_type = type_hints.get(name, str)
            pg_type = self._python_type_to_postgres(python_type)

            is_optional = get_origin(python_type) is Union and type(None) in get_args(python_type)

            if name == "id":
                col_defs.append("id SERIAL PRIMARY KEY")
                continue

            default = getattr(model_class, name, None)
            parts = [f"{name} {pg_type}"]

            if not is_optional:
                parts.append("NOT NULL")

            if default is not None and not is_optional:
                if isinstance(default, bool):
                    parts.append(f"DEFAULT {'TRUE' if default else 'FALSE'}")
                elif isinstance(default, str):
                    parts.append(f"DEFAULT '{default}'")
                else:
                    parts.append(f"DEFAULT {default}")

            col_defs.append(" ".join(parts))

        return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)});"

    def create_table_from_model(self, model_class, table_name: str) -> bool:
        if self._check_table_exists(table_name):
            return False

        sql = self._generate_create_table_sql(model_class, table_name)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql)
        return True

    def create_tables(self):
        from models.user import User
        from models.tables import Table
        from models.booking import Booking

        self.create_table_from_model(User, "users")
        self.create_table_from_model(Table, "tables")
        self.create_table_from_model(Booking, "bookings")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            try:
                self.conn.commit()
            except Exception:
                self.conn.rollback()
        else:
            self.conn.rollback()
