"""Tests for ConversationHistory multi-turn support."""

from core.llm import ConversationHistory


def test_empty_history():
    h = ConversationHistory()
    assert len(h) == 0
    assert h.get_messages() == []


def test_add_user_and_assistant():
    h = ConversationHistory()
    h.add_user("hello")
    h.add_assistant("hi there")
    msgs = h.get_messages()
    assert len(msgs) == 2
    assert msgs[0] == {"role": "user", "content": "hello"}
    assert msgs[1] == {"role": "assistant", "content": "hi there"}


def test_history_max_turns():
    h = ConversationHistory(max_turns=2)
    h.add_user("a")
    h.add_assistant("b")
    h.add_user("c")
    h.add_assistant("d")
    h.add_user("e")
    h.add_assistant("f")
    msgs = h.get_messages()
    assert len(msgs) == 4
    assert msgs[0]["content"] == "c"
    assert msgs[-1]["content"] == "f"


def test_clear():
    h = ConversationHistory()
    h.add_user("test")
    h.add_assistant("reply")
    h.clear()
    assert len(h) == 0
    assert h.get_messages() == []


def test_get_messages_returns_copy():
    h = ConversationHistory()
    h.add_user("hello")
    msgs = h.get_messages()
    msgs.append({"role": "user", "content": "injected"})
    assert len(h.get_messages()) == 1
