import pytest
from digitalguide.twilio.generateStates import CommandHandler
from digitalguide.twilio.generateStates import MessageHandler
from digitalguide.twilio.generateStates import TypeHandler
from digitalguide.twilio import generateStates


def test_messagehandler_with_pattern():
    yaml_dict = {"VEGAN_FRAGE": [{"action": "vegan_aufloesung",
                                 "filter": "regex",
                                  "handler": "MessageHandler",
                                  "regex": "WEITER_PATTERN"}]}

    actions = {"vegan_aufloesung": None}

    states = generateStates.read_state(yaml_dict, actions=actions)

    assert("VEGAN_FRAGE" in states.keys())
    assert(type(states["VEGAN_FRAGE"][0]) == MessageHandler)


def test_messagehandler_with_wrong_filter():
    yaml_dict = {"VEGAN_FRAGE": [{"action": "vegan_aufloesung",
                                 "filter": "regexxxx",
                                  "handler": "MessageHandler",
                                  "regex": "WEITER_PATTERN"}]}

    actions = {"vegan_aufloesung": None}

    with pytest.raises(NotImplementedError):
        states = generateStates.read_state(yaml_dict, actions=actions)


def test_with_wrong_handler():
    yaml_dict = {"VEGAN_FRAGE": [{"action": "vegan_aufloesung",
                                 "filter": "regex",
                                  "handler": "MessageHandlerxxxx",
                                  "regex": "WEITER_PATTERN"}]}

    actions = {"vegan_aufloesung": None}

    with pytest.raises(NotImplementedError):
        states = generateStates.read_state(yaml_dict, actions=actions)


def test_with_wrong_action():
    yaml_dict = {"VEGAN_FRAGE": [{"action": "vegan_aufloesungxxx",
                                 "filter": "regex",
                                  "handler": "MessageHandler",
                                  "regex": "WEITER_PATTERN"}]}

    actions = {"vegan_aufloesung": None}

    with pytest.raises(KeyError):
        states = generateStates.read_state(yaml_dict, actions=actions)


def test_commandhandler():
    yaml_dict = {"VEGAN_FRAGE": [{"action": "vegan_aufloesung",
                                  "command": "Weiter",
                                  "handler": "CommandHandler"}]}

    actions = {"vegan_aufloesung": None}

    states = generateStates.read_state(yaml_dict, actions=actions)

    assert("VEGAN_FRAGE" in states.keys())
    assert(type(states["VEGAN_FRAGE"][0]) == CommandHandler)

def test_typehandler():
    yaml_dict = {"FRAGE_QUIZ": [{"handler": "TypeHandler",
                                 "type": "Update",
                                 "action": "frage_quiz_tipp"}]}

    actions = {"frage_quiz_tipp": None}

    states = generateStates.read_state(yaml_dict, actions=actions)

    assert("FRAGE_QUIZ" in states.keys())
    assert(type(states["FRAGE_QUIZ"][0]) == TypeHandler)

def test_typehandler_with_wrong_type():
    yaml_dict = {"FRAGE_QUIZ": [{"handler": "TypeHandler",
                                 "type": "Updatexxx",
                                 "action": "frage_quiz_tipp"}]}

    actions = {"frage_quiz_tipp": None}

    with pytest.raises(NotImplementedError):
        states = generateStates.read_state(yaml_dict, actions=actions)
