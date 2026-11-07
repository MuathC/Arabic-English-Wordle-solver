"""
Game sessions for the web app.

A Game holds one secret word, the player's board, and any number of agent runs
on the same word. The agents are the unchanged classes from agents/; this module
only drives them (get_guess -> feedback -> update) the same way the desktop app does.
Games live in memory, so run the web app as a single process.
"""

import threading
import time
import uuid
from collections import OrderedDict

from agents.CSP_agent import CSP_agent
from agents.bayesian_agent import BayesianAgent
from agents.entropy_agent import EntropyAgent
from agents.frequency_agent import FrequencyAgent
from data.config import ALL_WORDS_ENGLISH, ALL_WORDS_ARABIC
from env.wordle_env import WordleEnv

AGENTS = {
    "CSP": CSP_agent,
    "Frequency": FrequencyAgent,
    "Bayesian": BayesianAgent,
    "Entropy": EntropyAgent,
}
WORDS = {"en": set(ALL_WORDS_ENGLISH), "ar": set(ALL_WORDS_ARABIC)}
MAX_GAMES = 200


class GameError(Exception):
    """A request the game can't accept. `code` is a message key the page translates."""

    def __init__(self, code, status=400):
        super().__init__(code)
        self.code = code
        self.status = status


def check_language(language):
    if not isinstance(language, str) or language not in WORDS:
        raise GameError("unknown_language")
    return language


def check_agent(agent_name):
    if not isinstance(agent_name, str) or agent_name not in AGENTS:
        raise GameError("unknown_agent")
    return AGENTS[agent_name]


def check_word(word, language):
    """Return the word normalised, or raise if it isn't a 5-letter word from the list."""
    word = word.strip().lower() if isinstance(word, str) else ""
    if len(word) < 5:
        raise GameError("not_enough_letters")
    if word not in WORDS[language]:
        raise GameError("not_in_word_list")
    return word


def board(env):
    return [{"word": word, "feedback": feedback} for word, feedback in zip(env.guesses, env.feedbacks)]


def status(env, done):
    if env.won:
        return "won"
    return "lost" if done else "playing"


class AgentRun:
    """One agent playing the game's secret word, one guess at a time."""

    def __init__(self, agent_cls, language, secret_word):
        self.agent = agent_cls(language=language)
        self.env = WordleEnv(language=language)
        self.env.reset(secret_word)
        self.gave_up = False
        self.seconds = 0.0
        self.lock = threading.Lock()

    @property
    def done(self):
        return self.env.game_over or self.gave_up

    def step(self):
        started = time.perf_counter()
        guess = self.agent.get_guess()
        if guess is None:  # CSP has no candidate left that fits the feedback
            self.gave_up = True
        else:
            feedback = self.env.guess(guess)
            if not self.env.game_over:
                self.agent.update(guess, feedback)
        self.seconds += time.perf_counter() - started
        if self.done:
            self.agent = None  # free the agent's word tables; the board is all we still need

    def state(self):
        return {
            "guesses": board(self.env),
            "status": status(self.env, self.done),
            "candidates_left": len(self.agent.candidates) if self.agent else None,
            "seconds": round(self.seconds, 2),
        }


class Game:
    def __init__(self, language, secret_word=None):
        self.id = uuid.uuid4().hex
        self.language = language
        self.player = WordleEnv(language=language)
        self.secret_word = self.player.reset(secret_word)
        self.runs = {}
        self.lock = threading.Lock()

    def player_state(self):
        state = {"guesses": board(self.player), "status": status(self.player, self.player.game_over)}
        if self.player.game_over:
            state["answer"] = self.secret_word
        return state

    def guess(self, word):
        with self.lock:
            if self.player.game_over:
                raise GameError("game_over", 409)
            self.player.guess(check_word(word, self.language))
            return self.player_state()

    def hint(self, agent_name):
        """The agent's next guess for the player's board so far."""
        agent = check_agent(agent_name)(language=self.language)
        with self.lock:
            if self.player.game_over:
                raise GameError("game_over", 409)
            history = list(zip(self.player.guesses, self.player.feedbacks))
        for word, feedback in history:
            agent.previous_guesses.append(word)  # as if the agent had made this guess itself
            agent.update(word, feedback)
        return agent.get_guess()

    def agent_step(self, agent_name, until_done=False):
        """Advance the agent's own game on this word by one guess, or to the end."""
        agent_cls = check_agent(agent_name)
        with self.lock:
            run = self.runs.get(agent_name)
            if run is None:
                run = self.runs[agent_name] = AgentRun(agent_cls, self.language, self.secret_word)
        with run.lock:  # per run, so different agents on one game can think at the same time
            if run.done:
                raise GameError("game_over", 409)
            run.step()
            while until_done and not run.done:
                run.step()
            return run.state()


_games = OrderedDict()
_games_lock = threading.Lock()


def create_game(language, secret_word=None):
    game = Game(language, secret_word)
    with _games_lock:
        _games[game.id] = game
        while len(_games) > MAX_GAMES:
            _games.popitem(last=False)
    return game


def get_game(game_id):
    with _games_lock:
        game = _games.get(game_id)
    if game is None:
        raise GameError("game_not_found", 404)
    return game

