-- Database roles for the free trial environment (D-54, D-61). Run ONCE as the owner role (the one in
-- QLAB_MIGRATION_DATABASE_URL), after the migrations have run or before; default privileges cover tables created later.
--
--   psql "$OWNER_URL" -v app_password='...' -v backup_password='...' -f infra/sql/app-role.sql
--
-- Role names are psql variables: -v app_role=qlab_app -v backup_role=qlab_backup (these are the defaults).
-- psql only (uses \set, \if, \gexec).
--
-- The attributes (LOGIN, NOSUPERUSER, ...) are set when the role is created. Re-running only resets the password: a
-- managed service's owner role is not a superuser and may not restate SUPERUSER (Neon, checked 2026-10-16).
-- Passwords come from psql variables; they are never written in this file. Re-running is safe:
-- existing roles keep their password unless you pass new values (then they are reset).
-- Neon: roles made in SQL are plain roles (not neon_superuser) and get only basic public-schema rights, which is what we want;
-- roles made in the console are neon_superuser members (https://neon.com/docs/manage/roles, checked 2026-10-16).
-- Do NOT create these two roles in the Neon console.

\set ON_ERROR_STOP on
\if :{?app_role}
\else
  \set app_role qlab_app
\endif
\if :{?backup_role}
\else
  \set backup_role qlab_backup
\endif

SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_role', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_role') \gexec
SELECT format('ALTER ROLE %I WITH PASSWORD %L', :'app_role', :'app_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_role') \gexec

SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'backup_role', :'backup_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'backup_role') \gexec
SELECT format('ALTER ROLE %I WITH PASSWORD %L', :'backup_role', :'backup_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'backup_role') \gexec

-- Connection and schema access.
SELECT format('GRANT CONNECT ON DATABASE %I TO %I, %I', current_database(), :'app_role', :'backup_role') \gexec
SELECT format('GRANT USAGE ON SCHEMA public TO %I, %I', :'app_role', :'backup_role') \gexec

-- The application: data changes only, no DDL, no ownership.
SELECT format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO %I', :'app_role') \gexec
SELECT format('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO %I', :'app_role') \gexec
-- Alembic's own bookkeeping table is the owner's business; the application does not need it.
-- (When the table is created after this script, infra/docker/api-start.sh revokes the default grants.)
SELECT format('REVOKE ALL ON TABLE public.alembic_version FROM %I', :'app_role')
WHERE to_regclass('public.alembic_version') IS NOT NULL \gexec

-- The backup: read only (pg_dump needs SELECT on tables and sequences).
SELECT format('GRANT SELECT ON ALL TABLES IN SCHEMA public TO %I', :'backup_role') \gexec
SELECT format('GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO %I', :'backup_role') \gexec

-- Tables and sequences the owner creates in later migrations are covered automatically.
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I', current_user, :'app_role') \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO %I', current_user, :'app_role') \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT ON TABLES TO %I', current_user, :'backup_role') \gexec
SELECT format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public GRANT SELECT ON SEQUENCES TO %I', current_user, :'backup_role') \gexec

-- Neither role may create objects in public (PostgreSQL 15+ already withholds this from PUBLIC; stated explicitly).
SELECT format('REVOKE CREATE ON SCHEMA public FROM %I, %I', :'app_role', :'backup_role') \gexec
