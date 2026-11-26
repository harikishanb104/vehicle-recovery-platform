import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"


def load_env(path: Path) -> None:
    """Load KEY=VALUE lines into the process environment.

    Existing variables win, so a shell export overrides the file.
    Missing file is fine: the database helper reports a missing URL later.
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env(ENV_FILE)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# The default is only for this local exercise. A deployed service must set JWT_SECRET.
JWT_SECRET = os.environ.get("JWT_SECRET", "local-dev-secret-change-me").strip()
TOKEN_HOURS = 12
