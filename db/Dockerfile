FROM postgres:18-alpine

ARG PGVECTOR_VERSION=v0.8.1

RUN apk add --no-cache --virtual .build-deps build-base git \
    && git clone --branch ${PGVECTOR_VERSION} --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && make -C /tmp/pgvector with_llvm=no OPTFLAGS="" \
    && make -C /tmp/pgvector with_llvm=no install \
    && rm -rf /tmp/pgvector \
    && apk del .build-deps
