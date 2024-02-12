#!/bin/bash

# To dump
# pg_dump -Fc -h localhost -p 15432 -U pgkogis bod_master > bod_master.sql

psql -h localhost -p 5432 -U postgres << SQL
DROP DATABASE bod_master;
SELECT 'CREATE DATABASE bod_master'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bod_master')\gexec
DO
\$do\$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'pgkogis') THEN

      RAISE NOTICE 'Role "pgkogis" already exists. Skipping.';
   ELSE
      CREATE ROLE pgkogis;
   END IF;
END
\$do\$;
DO
\$do\$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'www-data') THEN

      RAISE NOTICE 'Role "www-data" already exists. Skipping.';
   ELSE
      CREATE ROLE "www-data";
   END IF;
END
\$do\$;
DO
\$do\$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'bod_admin') THEN

      RAISE NOTICE 'Role "bod_admin" already exists. Skipping.';
   ELSE
      CREATE ROLE "bod_admin";
   END IF;
END
\$do\$;
DO
\$do\$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'rdsadmin') THEN

      RAISE NOTICE 'Role "rdsadmin" already exists. Skipping.';
   ELSE
      CREATE ROLE "rdsadmin";
   END IF;
END
\$do\$;
SQL

pg_restore -h localhost -p 5432 -U postgres -c -C -d bod_master bod_master.sql
