"""
CRUD (Create, Read, Update, Delete) operations for the e-commerce bot.

These functions encapsulate the database logic and are designed to be called
from within an active SQLAlchemy AsyncSession. They do not commit the session
themselves; the calling business logic (e.g., a bot handler) is responsible
for transaction management (commit/rollback).
"""

# Import all functions from submodules for backward compatibility
from .cart import *
from .catalog import *
from .orders import *
from .users import *