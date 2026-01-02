# agents/base_agent.py
from abc import ABC, abstractmethod
from data.config import ALL_WORDS_ENGLISH, ALL_WORDS_ARABIC


class BaseAgent(ABC):
    def __init__(self,language = "en"):
        self.language = language
        self.candidates = None
        pass

    @abstractmethod
    def reset(self):
        """Reset the agent’s state for a new game."""
        pass

    @abstractmethod
    def get_guess(self):
        """Return the agent’s next guess."""
        pass

    @abstractmethod
    def update(self, guess, feedback):
        """Update internal state based on feedback."""
        pass
    @abstractmethod
    def __str__(self):
        """String name of the agent."""
        pass

    def candidates(self,language = "en"):
        """Return a list of all possible candidates. Minding the language."""
        if self.language == "en":
            return ALL_WORDS_ENGLISH
        else:
            return ALL_WORDS_ARABIC