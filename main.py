import sys
import pathlib

# Ensure the backend package directory is on the Python path so imports like
# `from backend.main import app` and the relative imports used inside `backend.main`
# resolve correctly when this top‑level module is imported by the test suite.
_backend_dir = pathlib.Path(__file__).resolve().parent / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.append(str(_backend_dir))

# Import the FastAPI app defined in the backend's main module.
# The backend/main.py file defines a variable `app` which is the FastAPI instance.
from backend.main import app  # noqa: F401

# Re‑export the app at the top‑level so that `from main import app` works.
__all__ = ["app"]
