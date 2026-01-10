"""
Unit tests for the command management system.
"""

import pytest

from ecombot.core.commands import EcomBotCommandManager
from ecombot.core.messages import Language


@pytest.fixture
def command_manager():
    return EcomBotCommandManager(default_language=Language.EN)


def test_initialization_loads_commands(command_manager):
    """Test that commands are loaded upon initialization."""
    # Access private attribute for testing state
    assert Language.EN in command_manager._commands
    assert Language.ES in command_manager._commands
    assert Language.RU in command_manager._commands

    # Check content
    en_cmds = command_manager._commands[Language.EN]
    assert "start" in en_cmds
    assert "admin" in en_cmds


def test_get_commands_admin_role(command_manager):
    """Test fetching commands for admin role."""
    commands = command_manager.get_commands(role="admin", language=Language.EN)
    command_strings = {cmd.command for cmd in commands}

    assert "start" in command_strings
    assert "cart" in command_strings
    assert "orders" in command_strings
    assert "profile" in command_strings
    assert "admin" in command_strings
    assert "cancel" in command_strings


def test_get_commands_user_role(command_manager):
    """Test fetching commands for user role (should exclude admin commands)."""
    commands = command_manager.get_commands(role="user", language=Language.EN)
    command_strings = {cmd.command for cmd in commands}

    assert "start" in command_strings
    assert "cart" in command_strings
    assert "orders" in command_strings
    assert "profile" in command_strings

    # Admin-only commands should be absent
    assert "admin" not in command_strings
    assert "cancel" not in command_strings


def test_get_commands_language_fallback(command_manager):
    """Test fallback to default language if requested language is missing."""
    # FR is defined in Language enum but not populated in EcomBotCommandManager
    commands = command_manager.get_commands(role="user", language=Language.FR)

    # Should return EN commands (default)
    assert len(commands) > 0
    start_cmd = next(cmd for cmd in commands if cmd.command == "start")
    assert start_cmd.description == "🛍️ Browse catalog"  # English description


def test_get_commands_specific_language(command_manager):
    """Test fetching commands for a specific supported language."""
    commands = command_manager.get_commands(role="user", language=Language.ES)

    start_cmd = next(cmd for cmd in commands if cmd.command == "start")
    assert start_cmd.description == "🛍️ Explorar catálogo"  # Spanish description


def test_add_command(command_manager):
    """Test adding a new command dynamically."""
    command_manager.add_command(
        key="help", command="help", description="Get help", language=Language.EN
    )

    commands = command_manager.get_commands(role="user", language=Language.EN)
    command_strings = {cmd.command for cmd in commands}

    assert "help" in command_strings

    # Verify description
    help_cmd = next(cmd for cmd in commands if cmd.command == "help")
    assert help_cmd.description == "Get help"


def test_is_command_for_role_logic(command_manager):
    """Test the internal role check logic."""
    # Admin gets everything
    assert command_manager._is_command_for_role("admin", "admin") is True
    assert command_manager._is_command_for_role("cancel", "admin") is True
    assert command_manager._is_command_for_role("start", "admin") is True

    # User gets restricted
    assert command_manager._is_command_for_role("admin", "user") is False
    assert command_manager._is_command_for_role("cancel", "user") is False
    assert command_manager._is_command_for_role("start", "user") is True

    # Unknown role defaults to False
    assert command_manager._is_command_for_role("start", "guest") is False
