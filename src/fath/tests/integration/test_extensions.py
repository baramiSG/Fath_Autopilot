"""A2 running-version checks and A11 functional extension checks."""

from __future__ import annotations

import psycopg
import pytest
import redis

from fath.tests.conftest import redis_url, sync_database_url

pytestmark = pytest.mark.integration


def test_a2_postgres_major_and_extensions() -> None:
    with psycopg.connect(sync_database_url()) as conn:
        version = conn.execute("SELECT current_setting('server_version_num')::int").fetchone()
        assert version is not None
        assert 160000 <= version[0] < 170000
        exts = {row[0] for row in conn.execute("SELECT extname FROM pg_extension")}
        assert {"uuid-ossp", "vector", "age"} <= exts


def test_a2_redis_major_7() -> None:
    client = redis.Redis.from_url(redis_url())
    try:
        info = client.info("server")
        assert isinstance(info, dict)
        major = str(info["redis_version"]).split(".", 1)[0]
        assert major == "7"
    finally:
        client.close()


def test_a11_vector_hnsw_roundtrip() -> None:
    conn = psycopg.connect(sync_database_url())
    try:
        conn.execute(
            """
            CREATE TABLE synthetic_vec_tmp (
                id uuid PRIMARY KEY,
                embedding vector(1024)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX synthetic_vec_hnsw
            ON synthetic_vec_tmp USING hnsw (embedding vector_cosine_ops)
            """
        )
        conn.commit()
    finally:
        conn.execute("DROP TABLE IF EXISTS synthetic_vec_tmp")
        conn.commit()
        conn.close()


def test_a11_age_graph_cypher() -> None:
    conn = psycopg.connect(sync_database_url())
    created = False
    try:
        conn.execute("LOAD 'age'")
        conn.execute('SET search_path = ag_catalog, "$user", public')
        conn.execute("SELECT create_graph('synthetic_tmp_graph')")
        created = True
        rows = conn.execute(
            """
            SELECT * FROM cypher('synthetic_tmp_graph', $$
                CREATE (n:SyntheticNode {name: 'x'})
                RETURN n
            $$) AS (n agtype)
            """
        ).fetchall()
        assert len(rows) == 1
        conn.commit()
    finally:
        if created:
            try:
                conn.execute("LOAD 'age'")
                conn.execute('SET search_path = ag_catalog, "$user", public')
                conn.execute("SELECT drop_graph('synthetic_tmp_graph', true)")
                conn.commit()
            except psycopg.Error:
                conn.rollback()
        conn.close()
