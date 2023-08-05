# __init__.py

import os
from pathlib import Path

__all__ = []

from auto_screener.base import validate_requirement, dependencies

dependencies_path = dependencies()

if os.path.exists(dependencies_path):
    for source_file in os.listdir(dependencies_path):
        validate_requirement(
            source_file.replace("-", "_")[:source_file.rfind("-")],
            str(Path(dependencies_path) / Path(source_file)).replace(os.getcwd(), "")[1:]
        )
    # end for
# end if