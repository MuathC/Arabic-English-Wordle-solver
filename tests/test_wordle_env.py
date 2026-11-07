import pytest

from data.config import ALL_WORDS_ENGLISH
from env.wordle_env import MAX_GUESSES, SECRET_WORDS, WordleEnv, get_feedback

G, Y, X = "green", "yellow", "grey"


@pytest.mark.parametrize("guess, secret, expected", [
    ("crane", "crane", [G, G, G, G, G]),
    ("crane", "bumpy", [X, X, X, X, X]),
    ("nacre", "crane", [Y, Y, Y, Y, G]),
    # a repeated letter is only marked as often as the secret has it
    ("geese", "those", [X, X, X, G, G]),
    ("eerie", "theme", [Y, X, X, X, G]),
    ("speed", "abide", [X, X, Y, X, Y]),
    # Arabic: same rules, letter by letter
    ("كتابة", "كتابة", [G, G, G, G, G]),
    ("بتاكة", "كتابة", [Y, G, G, Y, G]),
])
def test_get_feedback(guess, secret, expected):
    assert get_feedback(guess, secret) == expected


def test_game_ends_on_win():
    env = WordleEnv("en")
    env.reset("crane")
    env.guess("slate")
    assert not env.game_over
    env.guess("crane")
    assert env.game_over and env.won and env.guess_count == 2


def test_game_ends_after_six_misses():
    env = WordleEnv("en")
    env.reset("crane")
    for _ in range(MAX_GUESSES):
        env.guess("slate")
    assert env.game_over and not env.won


def test_random_secrets_are_guessable():
    guessable = set(ALL_WORDS_ENGLISH)
    assert all(word in guessable for word in SECRET_WORDS["en"])
    assert WordleEnv("ar").secret_word in SECRET_WORDS["ar"]
