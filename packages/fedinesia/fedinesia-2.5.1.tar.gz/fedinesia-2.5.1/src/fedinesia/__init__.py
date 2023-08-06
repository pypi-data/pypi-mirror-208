"""Package 'fedinesia' level definitions."""
import sys
from typing import Any
from typing import Dict
from typing import Final

__version__: Final[str] = "2.5.1"
__display_name__: Final[str] = "Fedinesia"
__package_name__: Final[str] = __display_name__.lower()
USER_AGENT: Final[
    str
] = f"{__display_name__}_v{__version__}_Python_{sys.version.split()[0]}"

CLIENT_WEBSITE: Final[str] = "https://codeberg.org/MarvinsMastodonTools/fedinesia"

Status = Dict[str, Any]
