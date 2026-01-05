"""Core system components for centralized management."""

from .manager import manager
from .messages import Language
from .messages import MessageCategory


__all__ = ["manager", "Language", "MessageCategory"]
