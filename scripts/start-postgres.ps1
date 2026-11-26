# Start this project's Postgres cluster on port 5433 when it is not already listening.
# A postmaster.pid left by a killed process is removed first. The Windows
# PostgreSQL service on port 5432 is not touched.

$ErrorActionPreference = "Stop"

$PgCtl = "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe"
$DataDir = Join-Path $env:LOCALAPPDATA "vehicle-recovery-platform\pgdata"
$LogFile = Join-Path $env:LOCALAPPDATA "vehicle-recovery-platform\postgres.log"
$PidFile = Join-Path $DataDir "postmaster.pid"
$Port = 5433

$listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    exit 0
}

if (Test-Path $PidFile) {
    $recordedPid = 0
    $pidLine = (Get-Content -Path $PidFile -TotalCount 1).Trim()
    if ([int]::TryParse($pidLine, [ref]$recordedPid)) {
        $serverProcess = Get-Process -Id $recordedPid -ErrorAction SilentlyContinue
        if (-not $serverProcess) {
            Remove-Item -Path $PidFile -Force
        }
    }
}

& $PgCtl -D $DataDir -l $LogFile -o "-p $Port" start
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
