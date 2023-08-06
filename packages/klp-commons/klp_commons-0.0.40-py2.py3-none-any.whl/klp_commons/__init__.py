"""
Modulo Commons del ecosistema Kloop. Contiene los modulos de uso común para los paquetes 
(1) categorization
(2) reporting

PyPI URL:
"""
import sys
import logging

if sys.version_info[:2] >= (3, 10):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.10`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.40"

    log = logging.getLogger(__name__)