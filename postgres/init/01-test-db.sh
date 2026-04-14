#!/bin/bash
# Creates the strands_test database on first postgres container start
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE strands_test'
    WHERE NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'strands_test'
    )\gexec
    GRANT ALL PRIVILEGES ON DATABASE strands_test TO $POSTGRES_USER;
EOSQL
