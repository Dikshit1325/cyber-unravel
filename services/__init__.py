import sys
import pathlib

# Determine the path to the backend services directory.
_backend_services = pathlib.Path(__file__).resolve().parent.parent / "backend" / "services"
# Extend the package __path__ so that imports like `services.auth_service` resolve
# to modules inside the backend/services directory.
if _backend_services.is_dir():
    __path__.append(str(_backend_services))
