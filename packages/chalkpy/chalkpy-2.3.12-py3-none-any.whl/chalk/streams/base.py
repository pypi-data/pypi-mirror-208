from typing import Any


class StreamSource:
    """Base class for all stream sources generate from `@stream`."""

    def _config_to_json(self) -> Any:
        ...
