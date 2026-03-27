from dataclasses import dataclass
from typing import Any


@dataclass
class ServiceResult:
    success: bool
    message_key: str | None = None
    data: Any | None = None
