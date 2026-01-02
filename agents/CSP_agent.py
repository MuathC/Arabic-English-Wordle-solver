"""
CSP_agent (Constraint Satisfaction Agent)
-------------------------------------------
This agent uses a Constraint Satisfaction approach to solve Wordle.
It treats the problem as a process of elimination:
  - It starts with the full candidate word list.
  - After each guess, it updates the candidate list by filtering out words
    that would not produce the same feedback as the one received.
The algorithm is greedy in that it simply chooses a random candidate from
the remaining possibilities, relying on the filtering process to gradually
narrow down to the correct answer.
"""

import random
from agents.base_agent import BaseAgent
from data.config import ALL_WORDS_ENGLISH , ALL_WORDS_ARABIC


class CSP_agent(BaseAgent):
    def __init__(self, language="en"):
        # Initialize the base agent with the full word list.
        super().__init__()
        self.language = language
        # Create a copy of the word list to use as our working candidate pool.
        self.reset()

    def reset(self):
        """
        Reset the agent for a new game.
        Restores the candidate list to the full word list.
        """
        self.candidates = super().candidates(self.language)
        self.previous_guesses = []

    def get_guess(self):
        """
        Return a guess from the current candidate list.
        If there are candidates available, choose one at random.
        If not, return None.
        """
        guess = random.choice(self.candidates) if self.candidates else None
        self.previous_guesses.append(guess)
        return guess

    def update(self, guess, feedback):
        """
        Update the candidate list based on the feedback received for a guess.
        Keeps only those words that would produce the same feedback if guessed.
        """
        self.candidates = [word for word in self.candidates if self._is_consistent(word, guess, feedback) and word not in self.previous_guesses]
        #print(f"Remaining candidates: {len(self.candidates)}")

    def _is_consistent(self, candidate, guess, feedback):
        """
        Check if a candidate word is consistent with the feedback from a guess.
        This is done by computing the feedback for (guess, candidate) and comparing
        it to the observed feedback.
        Returns True if they match; otherwise, False.
        """
        return self._get_feedback(guess, candidate) == feedback

    def _get_feedback(self, guess, secret):
        """
        Compute the Wordle-style feedback for a given guess and secret word.
        Feedback is represented as a list with 3 possible values:
          - 'green': Correct letter in the correct position.
          - 'yellow': Correct letter but in the wrong position.
          - 'grey': Letter not present in the word.

        This function uses a two-pass algorithm:
          1. First, mark all positions where the guess exactly matches the secret (green).
          2. Then, for non-green positions, check if the guessed letter is present elsewhere in the secret.
             If so, mark it as yellow, ensuring each letter is only counted once.

        Returns:
            A list of feedback strings, one for each letter in the guess.
        """
        # Initialize feedback with 'grey' for each letter.
        feedback = ['grey'] * 5
        # Convert secret word into a list of letters for mutable operations.
        secret_list = list(secret)

        # First pass: Check for 'green' letters.
        for i in range(5):
            if guess[i] == secret[i]:
                feedback[i] = 'green'
                # Mark this letter as used by setting it to None.
                secret_list[i] = None

        # Second pass: Check for 'yellow' letters.
        for i in range(5):
            if feedback[i] == 'green':
                continue  # Skip positions already marked as green.
            if guess[i] in secret_list:
                feedback[i] = 'yellow'
                # Remove the letter from secret_list to prevent duplicate matches.
                secret_list[secret_list.index(guess[i])] = None

        return feedback
    
    def __str__(self):
        return "CSP"