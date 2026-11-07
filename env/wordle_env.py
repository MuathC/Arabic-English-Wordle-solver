"""
WordleEnv
---------
The Wordle game itself: holds the secret word, scores guesses and tracks when
the game is over. Used by the desktop UI, the benchmark and the web app.
"""

import random

from data.config import ALL_WORDS_ENGLISH, GAME_WORDS_ENGLISH, ALL_WORDS_ARABIC

MAX_GUESSES = 6

# English secrets come from the curated game list, minus the few game words that
# are missing from the guess list (the agents could never find those).
_english_guessable = set(ALL_WORDS_ENGLISH)
SECRET_WORDS = {
    "en": [word for word in GAME_WORDS_ENGLISH if word in _english_guessable],
    "ar": ALL_WORDS_ARABIC,
}


def get_feedback(guess, secret):
    """
    Wordle feedback for a guess against the secret word, one entry per letter:
    'green' (right letter, right spot), 'yellow' (in the word, wrong spot) or 'grey'.
    Repeated letters are only marked as often as they appear in the secret.
    """
    feedback = ['grey'] * len(guess)
    unmatched = list(secret)

    for i, letter in enumerate(guess):
        if letter == secret[i]:
            feedback[i] = 'green'
            unmatched[i] = None

    for i, letter in enumerate(guess):
        if feedback[i] != 'green' and letter in unmatched:
            feedback[i] = 'yellow'
            unmatched[unmatched.index(letter)] = None

    return feedback


class WordleEnv:
    def __init__(self, language="en"):
        if language not in SECRET_WORDS:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
        self.reset()

    def generate_random_word(self):
        return random.choice(SECRET_WORDS[self.language])

    def reset(self, secret_word=None):
        """Start a new game with the given secret word, or a random one. Returns the secret word."""
        self.secret_word = secret_word or self.generate_random_word()
        self.guesses = []
        self.feedbacks = []
        self.game_over = False
        return self.secret_word

    @property
    def guess_count(self):
        return len(self.guesses)

    @property
    def won(self):
        return bool(self.guesses) and self.guesses[-1] == self.secret_word

    def guess(self, word):
        """Score a guess and return its feedback list."""
        feedback = get_feedback(word, self.secret_word)
        self.guesses.append(word)
        self.feedbacks.append(feedback)
        self.game_over = word == self.secret_word or len(self.guesses) >= MAX_GUESSES
        return feedback

    def render(self):
        for word, feedback in zip(self.guesses, self.feedbacks):
            print(word, " ".join(feedback))
        print(f"Secret: {self.secret_word}\n")
