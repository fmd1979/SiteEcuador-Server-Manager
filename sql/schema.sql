-- Design for PostgreSQL 16+; illustrative schema, not deployed in v2.0 foundation.
CREATE TABLE organizations (
 id uuid PRIMARY KEY, name text NOT NULL, plan text NOT NULL DEFAULT 'trial', created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE users (
 id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organizations(id),
 email text NOT NULL, password_hash text NOT NULL, mfa_required boolean NOT NULL DEFAULT true,
 disabled_at timestamptz, UNIQUE(organization_id,email)
);
CREATE TABLE servers (
 id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organizations(id),
 display_name text NOT NULL, agent_id uuid UNIQUE NOT NULL, enabled boolean NOT NULL DEFAULT true
);
CREATE TABLE server_permissions (
 user_id uuid NOT NULL REFERENCES users(id), server_id uuid NOT NULL REFERENCES servers(id),
 permission text NOT NULL CHECK(permission IN ('view','operate','terminal','configure')),
 PRIMARY KEY(user_id,server_id,permission)
);
CREATE TABLE audit_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 organization_id uuid NOT NULL REFERENCES organizations(id), actor_id uuid REFERENCES users(id),
 server_id uuid REFERENCES servers(id), action text NOT NULL, result text NOT NULL,
 source_ip inet, created_at timestamptz NOT NULL DEFAULT now(), metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE terminal_sessions (
 id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organizations(id),
 user_id uuid NOT NULL REFERENCES users(id), server_id uuid NOT NULL REFERENCES servers(id),
 started_at timestamptz NOT NULL DEFAULT now(), ended_at timestamptz,
 approval_id uuid, session_recording_ref text
);
-- Production: enable RLS on tenant tables and enforce tenant scopes in every query.
