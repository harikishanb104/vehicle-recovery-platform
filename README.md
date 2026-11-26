# Plate Scan & Case Matching Service

A small full-stack slice of a vehicle-recovery platform. Truck cameras post plate scans. The API stores every scan, attaches it to an active case when this agency already tracks the VIN, or asks a mock lender network whether a new claimable case should be opened. Staff sign in and work only with their own agency's cases, plus pending cases that no agency owns yet.

## Run it locally

Requirements: Python 3.12, Node.js 22, and the PostgreSQL 17 binaries (already installed on this PC as `C:\Program Files\PostgreSQL\17`).

This project uses its own Postgres cluster on port **5433**, with data in `%LOCALAPPDATA%\vehicle-recovery-platform\pgdata`. The Windows PostgreSQL service on port 5432 is not used. Local connections to 5433 do not require a password. `backend/.env` points at that cluster.

The scheduled task `vehicle-recovery-postgres` starts that cluster when you sign in to Windows. Register it once from this repo:

```powershell
$script = "c:\vehicle-recovery-platform\scripts\start-postgres.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "vehicle-recovery-postgres" -Action $action -Trigger $trigger -Principal $principal -Description "Start the vehicle-recovery Postgres cluster on port 5433"
```

Start it now, or any time it is stopped:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File c:\vehicle-recovery-platform\scripts\start-postgres.ps1
```

In pgAdmin, use host `127.0.0.1`, port `5433`, maintenance database `postgres`, and username `postgres`. Type `postgres` in the password box and check **Save password**. This cluster does not check that password; pgAdmin only stops asking after a password is saved on a successful connection. Then open the database `vehicle_recovery`. Do not connect pgAdmin to port 5432.

Backend:

```powershell
cd c:\vehicle-recovery-platform
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python create_database.py
python create_tables.py
python seed.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend, in a second terminal:

```powershell
cd c:\vehicle-recovery-platform\frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. The dev server proxies `/api` and `/mock` to the API.

If the virtual environment does not exist yet:

```powershell
py -m venv .venv
```

If the port 5433 cluster does not exist yet, create it once with `initdb` from the PostgreSQL 17 `bin` folder, then start it on port 5433 as above. `create_database.py` creates the empty `vehicle_recovery` database. `create_tables.py` creates the five tables and is safe to run again.

## Demo accounts

Both passwords are `demo-pass`.

| Username | Agency | Camera |
|---|---|---|
| agent.a | Agency A | cam_1001 |
| agent.b | Agency B | cam_2050 |

Agency A already has an active case for VIN `1FTFW1E51NFA12345`, with three older scans. Agency B has no case for VIN `5NPE34AF9KH123456`.

Existing-case flow (no login):

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/scans -H "Content-Type: application/json" -d "{\"camera_id\":\"cam_1001\",\"plate\":\"7XYZ123\",\"vin\":\"1FTFW1E51NFA12345\",\"latitude\":33.749,\"longitude\":-84.388,\"scanned_at\":\"2026-09-04T16:00:00Z\",\"image_url\":\"https://example.com/scans/new.jpg\"}"
```

New-case flow:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/scans -H "Content-Type: application/json" -d "{\"camera_id\":\"cam_2050\",\"plate\":\"8ABC999\",\"vin\":\"5NPE34AF9KH123456\",\"latitude\":33.75,\"longitude\":-84.39,\"scanned_at\":\"2026-09-04T12:00:00Z\",\"image_url\":\"https://example.com/scans/new.jpg\"}"
```

Sign in as `agent.a`, open Available to claim, and claim the case that Agency B's camera opened. Sign in as `agent.b` afterward: that case is no longer listed, and opening it by id is refused.

## Assumptions

- `pending_claim` has no owning tenant. `scanned_by_tenant_id` records which agency's camera opened the case. Ownership (`tenant_id` and `assigned_user_id`) is set only when someone claims.
- Only one open case may exist for a VIN. A closed case can be followed by a new one.
- The location trail is every stored scan for that VIN, oldest first, including scans from another agency. The caller must be allowed to see the case first: their own cases at any status, or any `pending_claim` case.
- A VIN ending in `0` is not eligible. The VIN `00000000000000000` stands for a partner-network failure. The scan is stored either way, and no case is created. Other VINs, including both samples in the case study, are eligible.
- An unknown `camera_id` is rejected and nothing is stored. Cameras are not given an active/inactive flag.
- Login is a username, a password, and a JWT. The tenant id is read from the user row. The scan endpoint stays unauthenticated.
- Staff and admin may both claim. The demo users are staff.
- Two claims on the same case lock the row. One succeeds. The other receives a conflict.
- Images are a URL string. Notifications are not sent. A production version would publish a domain event after a claim and after a new pending case, and a worker would email the agency. That worker is not in this repo.

## What is left out

Real camera hardware, a real lender integration, a third-party identity provider, image upload, notification delivery, map rendering, and any AWS deployment. The deployment sketch is in [DESIGN.md](DESIGN.md).

`seed.py` does nothing if Agency A is already present, so it will not reset data you have added by posting scans.
