-- Database roles for the free trial environment (D-54, D-61). Run ONCE as the owner role (the one in
-- QLAB_MIGRATION_DATABASE_URL), after the migrations have run or before; default privileges cover tables created later.
--
--   psql "$OWNER_URL" -v app_password='...' -v backup_password='...' -f infra/sql/app-role.sql
--
-- Passwords come from psql variables; they are never written in this file. Re-running is safe:
-- existing roles keep their password unless you pass new values (then they are reset).
-- Neon: roles made in SQL are plain roles (not neon_superuser) and get only basic public-schema rights, which is what we want;
-- roles made in the console are neon_superuser members (https://neon.com/docs/manage/roles, checked 2026-10-16).
-- Do NOT create these two roles in the Neon console.

\set ON_ERROR_STOP on

SELECT format('CREATE ROLE qlab_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'qlab_app') \gexec
SELECT format('ALTER ROLE qlab_app WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'qlab_app') \gexec

SELECT format('CREATE ROLE qlab_backup LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'backup_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'qlab_backup') \gexec
SELECT format('ALTER ROLE qlab_backup WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'backup_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'qlab_backup') \gexec

-- Connection and schema access.
SELECT format('GRANT CONNECT ON DATABASE %I TO qlab_app, qlab_backup', current_database()) \gexec
GRANT USAGE ON SCHEMA public TO qlab_app, qlab_backup;

-- The application: data changes only, no DDL, no ownership.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO qlab_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO qlab_app;
-- Alembic's own bookkeeping table is the owner's business; the application does not need it.
SELECT 'REVOKE ALL ON TABLE public.alembic_version FROM qlab_app'
WHERE to_regclass('public.alembic_version') IS NOT NULL \gexec

-- The backup: read only (pg_dump needs SELECT on tables and sequences).
GRANT SELECT ON ALL TABLES IN SCHEMA public TO qlab_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO qlab_backup;

-- Tables and sequences the owner creates in later migrations are covered automatically.
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO qlab_app', current_user) \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO qlab_app', current_user) \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT ON TABLES TO qlab_backup', current_user) \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT ON SEQUENCES TO qlab_backup', current_user) \gexec

-- Neither role may create objects in public (PostgreSQL 15+ already withholds this from PUBLIC; stated explicitly).
REVOKE CREATE ON SCHEMA public FROM qlab_app, qlab_backup;
