"""
Unit tests for the core message management system.
"""

import pytest

from ecombot.core.messages import BaseMessageManager
from ecombot.core.messages import Language


class ConcreteMessageManager(BaseMessageManager):
    """Concrete implementation of BaseMessageManager for testing."""

    def _load_messages(self) -> None:
        self._messages = {
            Language.EN: {
                "hello": "Hello, {name}!",
                "welcome": "Welcome to the bot.",
                "only_en": "Only in English",
            },
            Language.ES: {
                "hello": "Hola, {name}!",
                "welcome": "Bienvenido al bot.",
            },
        }


@pytest.fixture
def message_manager():
    return ConcreteMessageManager(default_language=Language.EN)


def test_initialization(message_manager):
    """Test that messages are loaded upon initialization."""
    assert Language.EN in message_manager._messages
    assert Language.ES in message_manager._messages
    assert message_manager.default_language == Language.EN


def test_get_message_success(message_manager):
    """Test retrieving a message in the requested language."""
    msg = message_manager.get_message("welcome", language=Language.ES)
    assert msg == "Bienvenido al bot."


def test_get_message_formatting(message_manager):
    """Test message formatting with arguments."""
    msg = message_manager.get_message("hello", language=Language.EN, name="Alice")
    assert msg == "Hello, Alice!"

    msg_es = message_manager.get_message("hello", language=Language.ES, name="Bob")
    assert msg_es == "Hola, Bob!"


def test_get_message_fallback_to_default_language(message_manager):
    """Test fallback to default language if key is missing in requested language."""
    # 'only_en' exists in EN but not ES
    msg = message_manager.get_message("only_en", language=Language.ES)
    assert msg == "Only in English"


def test_get_message_fallback_to_key(message_manager):
    """Test fallback to key if message is missing in all languages."""
    msg = message_manager.get_message("non_existent_key", language=Language.EN)
    assert msg == "non_existent_key"


def test_get_message_formatting_error(message_manager):
    """Test handling of formatting errors (e.g. missing kwargs)."""
    # Missing 'name' argument
    msg = message_manager.get_message("hello", language=Language.EN)
    # Should return the unformatted string instead of raising an error
    assert msg == "Hello, {name}!"


def test_add_message(message_manager):
    """Test adding a new message dynamically."""
    message_manager.add_message("new_key", "New Message", Language.EN)
    msg = message_manager.get_message("new_key", language=Language.EN)
    assert msg == "New Message"

    # Add for a new language
    message_manager.add_message("new_key", "Nouveau Message", Language.FR)
    msg_fr = message_manager.get_message("new_key", language=Language.FR)
    assert msg_fr == "Nouveau Message"


def test_get_supported_languages(message_manager):
    """Test retrieving supported languages."""
    langs = message_manager.get_supported_languages()
    assert Language.EN in langs
    assert Language.ES in langs
    # FR is not loaded initially in ConcreteMessageManager
    assert Language.FR not in langs
