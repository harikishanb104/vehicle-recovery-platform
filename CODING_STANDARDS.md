# Coding standards

This file is the bar for code in this repository. Read it before adding a feature. New code follows it on the first commit, not in a later cleanup pass.

The service is a small plate-scan and case-matching API. Clarity beats cleverness. A teammate who opens one file should be able to say what that file is responsible for, and what business rule it protects, without reading the rest of the project.

## Layout

Python backend code lives under `backend/app/`. Responsibilities do not share a file.

| Folder | What belongs here | What does not |
|---|---|---|
| `models/` | SQLAlchemy tables, relationships, and database constraints | HTTP shapes, request checks, queries that serve one endpoint |
| `schemas/` | Pydantic models for data crossing the API boundary | SQL, session use, tenant lookups |
| `validation/` | Rules for a single value: VIN, plate, coordinates, camera id | Knowledge of who is logged in, or whether a row exists |
| `database.py` | Engine, connection check, creating tables | Business decisions about cases or scans |

Later endpoint work gets its own folders, and those folders stay separate too:

| Folder | Responsibility |
|---|---|
| `services/` | One use case per class. Decides the branch (existing case or new case) and calls the database |
| `api/` | FastAPI routes. Reads the caller, calls one service, returns one schema |

The React app, when we build the dashboard, uses the same idea: `src/api/` for HTTP calls, `src/pages/` for screens, `src/components/` for pieces reused by more than one screen. A page does not build its own fetch URL inline.

Do not add a folder, a base class, or an interface until a second real caller needs it.

## How a file should read

- One concept per module. `models/case.py` is the recovery case. It does not also define a scan.
- Public functions and classes take type hints and return a concrete type.
- Names match the case study: tenant, camera, case, scan, `pending_claim`, `active`, `closed`.
- Prefer a straight sequence of steps over a helper that is used once.
- Raise a specific error and let the route turn it into an HTTP response. Do not return `None` for "the caller is not allowed to see this."
- Keep secrets in `backend/.env`. Do not print `DATABASE_URL`, password hashes, or tokens.

## Comments

Every class and every function has a docstring. The docstring answers two questions:

1. What job does this do for the product?
2. What rule is enforced here that the name alone does not show?

Write that in plain sentences. Mention the tenant boundary, the claim exception, or the reason a column is nullable when that is the point of the code.

An inline comment is for a constraint or a choice that would surprise a reader. Do not comment an import, a loop, an assignment, or a line that already says what it does.

```python
# Useful: the column is easy to misread.
# Ownership stays empty until a staff user claims the case.
tenant_id: Mapped[int | None]

# Noise: restates the next line.
# Set the status to active.
case.status = CaseStatus.ACTIVE
```

## Object-oriented shape

- A table is a class. A value rule is a class with a `parse` method that returns the cleaned value or raises `ValueError`.
- Use inheritance only to remove real duplication. `TimestampMixin` exists because several tables store `created_at` the same way. Do not invent a parent class for two unrelated models.
- A model does not import FastAPI. A schema does not import the engine. A validator does not import a model.

## SOLID, applied here

- **Single responsibility.** A route authenticates and delegates. A service performs one use case. A model describes one table.
- **Open for extension.** A new case status is a new enum value plus the constraint that says who may own it. Callers branch on the enum, not on raw strings.
- **Liskov.** Subclasses and mixins must be usable wherever the parent is used. Do not override a mixin so that one table silently stops storing `created_at`.
- **Interface segregation.** Pass the session and the specific inputs a use case needs. Do not pass the whole request, or a "context" object that holds everything.
- **Dependency direction.** Routes depend on services. Services depend on models and the session. Models depend on nothing in `api/` or `services/`.

## Database rules

- The database enforces ownership, uniqueness, and ranges. Python validation is a clearer error for the caller, not the only lock.
- Foreign keys use `ON DELETE RESTRICT`. A tenant, camera, or case is not removed by accident while scans still point at it.
- Index every foreign key and every column we filter or sort on (`vin`, `status`, `scanned_at`).
- Store times in `timestamptz`. Reject a timestamp that has no timezone.
- Store a VIN and a plate in one canonical form (trimmed, uppercase) so the same vehicle does not split into two keys.

## What we will not merge

- A comment that repeats the function name.
- A class with a single method that only forwards to another function, added "for architecture."
- Business rules copied into both the route and the service.
- A catch-all `except Exception` that hides a programming error. Convert known failures; let the rest surface.
- Generated scaffolding left empty "for later." A new file has real code, or it is not added yet.
