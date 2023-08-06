import sys
from pathlib import Path

from dynaconf import LazySettings

SCHEMAS_DEFAULTS = Path(__file__).parent.joinpath("resources", "defaults.toml")

SCHEMAS_DOCS = Path(__file__).parent.joinpath("resources", "documentation.toml")

conf = LazySettings(
    SETTINGS_FILE_FOR_DYNACONF=[str(SCHEMAS_DEFAULTS), str(SCHEMAS_DOCS)],
)
