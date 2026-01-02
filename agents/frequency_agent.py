"""
FrequencyAgent
--------------
AI Algorithm Used: Greedy Heuristic Search using Letter Frequency Analysis

This agent uses a simple yet effective strategy to solve Wordle:
1. It computes the frequency of each letter among the current candidate words.
2. Each candidate word is scored by summing the frequencies of its unique letters.
3. The word with the highest total score is chosen as the next guess.

After each guess, the agent updates its candidate list by filtering out words that are
inconsistent with the feedback received.
"""

from agents.base_agent import BaseAgent
from data.config import ALL_WORDS_ENGLISH,ALL_WORDS_ARABIC
import random

class FrequencyAgent(BaseAgent):
    def __init__(self,language="en"):
        """
        Initialize the agent with the list of allowed words.

        Args:
            all_words (list): A list of allowed 5-letter words.
        """
        # Store a copy of the allowed words for internal use.
        super().__init__()
        self.previous_guesses = []
        self.language = language
        # Initialize the candidate list by calling reset.
        self.reset()

    def reset(self):
        """
        Resets the agent for a new game.

        This method resets the candidate list to the full list of allowed words,
        preparing the agent for a new game.
        """
        self.candidates = super().candidates(language=self.language)
        self.previous_guesses = []

    def get_guess(self):
        """
        Choose the next guess based on letter frequency among the current candidates.
        If all candidates have the same score, a random guess is chosen.

        Returns:
            str: The word with the highest score according to letter frequency, or a random word if scores are equal.

        The method works by:
          1. Calculating how often each letter appears in the candidate words.
          2. Scoring each candidate by summing the frequency of its unique letters.
          3. Returning the candidate with the highest total score.
        """
        # If no candidates remain, reset the candidate list.
        if not self.candidates:
            self.candidates = ALL_WORDS_ARABIC

        # Compute frequency of each letter across all candidate words.
        frequency = {}
        for word in self.candidates:
            for letter in word:
                frequency[letter] = frequency.get(letter, 0) + 1

        # Score each candidate by summing the frequency of its unique letters.
        best_score = -1
        best_candidates = []

        for word in self.candidates:
            # Using set(word) to ensure each letter is only counted once.
            score = sum(frequency.get(letter, 0) for letter in set(word))

            # Check if this candidate has the best score
            if score > best_score:
                best_score = score
                best_candidates = [word]  # reset to this new best candidate
            elif score == best_score:
                best_candidates.append(word)  # add this word to the list of best candidates

        # If multiple candidates have the same best score, pick randomly
        best_word = random.choice(best_candidates)
        self.previous_guesses.append(best_word)
        return best_word

    def update(self, guess, feedback):
        """
        Update the candidate list based on the guess and the feedback received.

        Args:
            guess (str): The word that was guessed.
            feedback (list): A list of 5 strings representing the feedback ("green", "yellow", or "grey").

        The update is performed by filtering the current candidate list and retaining only the words
        that would produce the same feedback as received if they were the secret word.
        """
        self.candidates = [word for word in self.candidates if self.match_feedback(word, guess, feedback) and word not in self.previous_guesses]

    def match_feedback(self, word, guess, feedback):
        """
        Check if a candidate word is consistent with the feedback provided for a given guess.

        This function implements a simplified version of feedback matching:
          - For "green": the letter must match at that exact position.
          - For "yellow": the letter must appear somewhere in the word, but not in that position.
          - For "grey": the letter must not appear in the word at all.

        Note: This simplified approach does not handle multiple occurrences of letters perfectly.
        when you read this and have questions while I followed this approach across the project I can explain it then

        Args:
            word (str): A candidate word to test.
            guess (str): The guessed word.
            feedback (list): The feedback list for the guess.

        Returns:
            bool: True if the candidate is consistent with the feedback; False otherwise.
        """
        for i, (letter, fb) in enumerate(zip(guess, feedback)):
            if fb == "green":
                if word[i] != letter:
                    return False
            elif fb == "yellow":
                # Letter must appear in the word but not at the same position.
                if letter not in word or word[i] == letter:
                    return False
            elif fb == "grey":
                # For simplicity, assume grey means the letter is not in the word at all.
                if letter in word:
                    return False
        return True
    
    def __str__(self):
        return "Frequency"