import pytest
from ai_persona_bot import PersonaBot

def test_bot_initialization():
    bot = PersonaBot("test_token")
    assert bot is not None
    assert bot.voice_enabled == {}
