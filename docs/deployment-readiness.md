# Deployment Readiness

## Purpose

This document defines Layer 11 deployment readiness options and blockers.
It is planning guidance only. No production deployment is implemented by this
prompt.

## Current Local Development Reality

Careero currently runs as a local-first FastAPI backend, React + Vite frontend,
PostgreSQL database, Alembic migrations, local scripts, and local health checks.
The `infra/` directory is reserved for future infrastructure notes and does not
contain production cloud deployment logic.

Careero is not production-ready.

## Deployment Target Options

| Option | Requirements | Risks | Missing pieces | Security/privacy implications | Operational burden | Recommended timing |
| --- | --- | --- | --- | --- | --- | --- |
| Local-only packaged app | Local install/run packaging, local backup notes, clear local data location, upgrade path. | User support complexity, local environment drift, data loss if backups are unclear. | Packaging, backup/restore docs, local migration UX. | Data stays local by default, but device security is user-managed. | Low to medium. | Possible after workflow and artifact lifecycle stabilize. |
| Single-user hosted app | Auth for one owner, secrets management, hosted DB, backups, monitoring, export/delete design. | False sense of production readiness, weak isolation if later shared. | Auth, account lifecycle, backups, monitoring, deployment runbook. | Private data leaves local machine and needs provider/privacy review. | Medium. | Future controlled experiment only. |
| Private hosted beta | Real auth, account/workspace authorization, tenant isolation, retention, export/delete, cost controls, support. | Privacy incidents, cost spikes, data deletion gaps, support load. | Most Layer 11 implementation blockers. | Requires clear privacy policy, logging rules, user support, and incident process. | Medium to high. | Future after Layer 4/6 stabilization and Layer 11 approvals. |
| Production multi-tenant SaaS | Hardened auth, authorization, tenancy, billing if paid, backups, rollback, monitoring, incident response, support, legal/privacy review. | High trust, security, compliance, and operational risk. | Production auth/billing/deployment/account lifecycle/privacy controls. | Full hosted SaaS obligations. | High. | Future, after private beta proves durable value. |

## Required Production Capabilities

- Authentication.
- Authorization.
- Tenant isolation.
- Secrets management.
- Environment model.
- Database migration process.
- Backup/restore.
- Monitoring.
- Logging.
- Incident response.
- Cost controls.
- Data export/delete.
- Privacy and retention policy.
- AI usage controls.

## Environment Model

Future hosted deployment should define separate local, test, staging/private
beta, and production environments. Each environment needs distinct secrets,
database URLs, AI provider keys, feature flags, logging controls, and cost
budgets.

## Database Migrations

Production readiness requires:

- Migration runbook.
- Backup-before-migration process.
- Rollback or forward-fix expectations.
- Compatibility windows for Role-backed Opportunity persistence.
- Test database validation.

No migration changes are included in this Layer 11 readiness prompt.

## Monitoring and Logging

Hosted modes need health checks, application error reporting, database health,
AI provider error/cost visibility, background job visibility if future workers
exist, and privacy-safe logs. Logs must avoid raw resumes, private notes, raw
prompts, API keys, and raw job descriptions unless a separately approved support
mode exists.

## Rollback Expectations

Future deployments need:

- Versioned release artifacts.
- Database backup before risky migrations.
- Feature flags for AI and external integrations.
- Documented rollback and forward-fix process.
- User communication process for incidents.

## Explicit Non-Implementation Statement

This prompt does not implement hosted deployment, production infrastructure,
Docker/Kubernetes/Terraform/cloud resources, production auth, billing, account
deletion/export, retention enforcement, or external integrations.
