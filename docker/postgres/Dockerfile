# Postgres 16 + Apache AGE + pgvector
#
# Pin sources (resolved 2026-08-27):
# - Base image: docker.io/library/postgres:16
#   index digest from `docker buildx imagetools inspect postgres:16`
#   (official library, version annotation 16.15)
# - pgvector: git commit 8ee86c96f0fd72390f890aa8a336fda6d3ab4c6c
#   (GitHub tag v0.8.6 object; https://github.com/pgvector/pgvector/commit/8ee86c96f0fd72390f890aa8a336fda6d3ab4c6c)
# - Apache AGE: git commit 2db2f060c4c9265a14d40f007eb8c56febf31e4c
#   (GitHub tag PG16/v1.6.0-rc0 object; https://github.com/apache/age/commit/2db2f060c4c9265a14d40f007eb8c56febf31e4c)

FROM postgres:16@sha256:f1c3376c26f2609ab9f29f71f824103fe2fcd8ee0346485cb6122a4f93df6f94

ARG PGVECTOR_COMMIT=8ee86c96f0fd72390f890aa8a336fda6d3ab4c6c
ARG AGE_COMMIT=2db2f060c4c9265a14d40f007eb8c56febf31e4c

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        bison \
        build-essential \
        ca-certificates \
        flex \
        git \
        postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# pgvector — fetch the immutable commit (not a mutable tag)
WORKDIR /tmp/pgvector-src
RUN git clone --no-checkout https://github.com/pgvector/pgvector.git . \
    && git fetch --depth 1 origin "${PGVECTOR_COMMIT}" \
    && git checkout "${PGVECTOR_COMMIT}" \
    && test "$(git rev-parse HEAD)" = "${PGVECTOR_COMMIT}" \
    && make \
    && make install

# Apache AGE — fetch the immutable commit (not a mutable tag)
WORKDIR /tmp/age-src
RUN git clone --no-checkout https://github.com/apache/age.git . \
    && git fetch --depth 1 origin "${AGE_COMMIT}" \
    && git checkout "${AGE_COMMIT}" \
    && test "$(git rev-parse HEAD)" = "${AGE_COMMIT}" \
    && make \
    && make install

WORKDIR /
RUN rm -rf /tmp/pgvector-src /tmp/age-src \
    && apt-get purge -y --auto-remove \
        bison \
        build-essential \
        flex \
        git \
        postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

CMD ["postgres", "-c", "shared_preload_libraries=age"]
