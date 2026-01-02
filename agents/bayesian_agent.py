"""
BayesianAgent (Bayesian Updating Agent)
-----------------------------------------
AI Algorithm Used: Bayesian Updating with a Smooth Likelihood Function

This agent applies Bayesian reasoning to update the probability of each candidate word
being the secret word based on the feedback it receives after each guess. It maintains
a probability distribution over all possible words and uses Bayes' theorem to adjust
these probabilities. The likelihood of each candidate is computed by comparing the
predicted feedback (if that candidate were the true word) with the actual feedback
received, using an exponential decay function based on the number of mismatches. This
approach results in a smooth likelihood that helps the agent refine its candidate set
gradually.
"""

import math
from agents.base_agent import BaseAgent
from data.config import ALL_WORDS_ENGLISH,ALL_WORDS_ARABIC
import random

class BayesianAgent(BaseAgent):
    def __init__(self,language="en"):
        """
        Initialize the BayesianAgent with the full list of possible words.

        Args:
            word_list (list): A list of candidate words.
        """
        super().__init__()
        self.language = language
        self.previous_guesses = []
        # Initialize the agent state.
        self.reset()

    def reset(self):
        """
        Reset the agent for a new game.
        Sets the candidate list back to the full word list and assigns a uniform probability
        distribution over all candidates.
        """
        self.candidates = super().candidates(language=self.language)
        self.previous_guesses = []
        # Initially, assign each candidate a probability of 1.0.
        self.probabilities = {word: 1.0 for word in self.candidates}
        self.normalize_probabilities()

    def normalize_probabilities(self):
        """
        Normalize the candidate probabilities so that the total probability sums to 1.
        This is done by dividing each candidate's probability by the total probability.
        """
        total = sum(self.probabilities.values())
        if total > 0:
            for word in self.probabilities:
                self.probabilities[word] /= total

    def get_guess(self):
        """
        Return the next guess based on the current probability distribution.
        The guess is selected as the candidate with the highest posterior probability.
        If all guesses have the same probability, a random guess is selected.

        Returns:
            str: The word with the highest probability, or a random word if all probabilities are equal.
        """
        # Get the maximum probability value
        max_prob = max(self.probabilities.values(), default=0)

        # Find all candidates with the maximum probability
        best_candidates = [word for word, prob in self.probabilities.items() if prob == max_prob]

        # If all candidates have the same probability, select a random guess
        if len(best_candidates) == len(self.candidates):
            best_guess = random.choice(self.candidates)
        else:
            best_guess = random.choice(best_candidates)

        self.previous_guesses.append(best_guess)
        return best_guess

    def update(self, guess, feedback):
        """
        Update the candidate probabilities using Bayes' theorem based on the feedback received.

        For each candidate word, compute the likelihood of the observed feedback given that
        candidate. Multiply the candidate's existing probability by the likelihood and then
        normalize the distribution.

        Args:
            guess (str): The word that was guessed.
            feedback (list): The list of feedback strings received (e.g., ['green', 'grey', 'yellow', ...]).
        """
        new_probabilities = {}
        for word in self.candidates:
            likelihood = self.likelihood(word, guess, feedback)
            new_probabilities[word] = self.probabilities[word] * likelihood

        # Filter out candidates with extremely low probability to avoid numerical issues.
        self.probabilities = {word: prob for word, prob in new_probabilities.items() if prob > 1e-8 and word not in self.previous_guesses}
        self.normalize_probabilities()
        # Update the candidate list to include only those with non-negligible probabilities.
        self.candidates = list(self.probabilities.keys())
        #print(f"Remaining candidates: {len(self.candidates)}")


    def likelihood(self, candidate, guess, feedback):
        """
        Compute the likelihood of observing the given feedback if the candidate were the true word.

        Instead of a binary likelihood (1.0 if the feedback matches exactly, 0.0 otherwise),
        we calculate an error score as the number of mismatches between the predicted feedback
        and the observed feedback. Then, we convert that error into a likelihood value using
        an exponential decay function: likelihood = exp(-error).

        Example:
            If predicted_feedback = ['green', 'grey', 'yellow', 'grey', 'green']
            and observed_feedback = ['green', 'yellow', 'grey', 'grey', 'green'],
            there are 2 mismatches, so error = 2 and likelihood = exp(-2).

        Args:
            candidate (str): A candidate word.
            guess (str): The guessed word.
            feedback (list): The observed feedback for the guess.

        Returns:
            float: The likelihood value for the candidate.
        """
        # Step 1: Get the feedback we'd expect if this candidate were the correct word
        predicted_feedback = self.compute_feedback(candidate, guess)

        # Step 2: Count how many feedback positions differ from what was observed
        error_count = 0
        for predicted, observed in zip(predicted_feedback, feedback):
            if predicted != observed:
                error_count += 1

        # Step 3: Convert the error count to a likelihood using exp decay.
        # Fewer errors = higher likelihood
        
        likelihood_score = math.exp(-error_count)
        return likelihood_score

    def compute_feedback(self, candidate, guess):
        """
        Compute the Wordle-style feedback for a given candidate word and guess.

        This function uses a two-pass algorithm:
          1. First pass: Mark letters that are correct and in the correct position as 'green'.
          2. Second pass: For letters not already marked 'green', mark them 'yellow' if they
             appear elsewhere in the candidate (only counting each occurrence once), otherwise 'grey'.

        Args:
            candidate (str): The candidate word (hypothetical secret word).
            guess (str): The guessed word.

        Returns:
            tuple: A tuple of feedback strings (e.g., ('green', 'grey', 'yellow', 'grey', 'green')).
        """
        feedback = [None] * len(guess)
        # Make a mutable copy of candidate letters to track used letters.
        candidate_letters = list(candidate)

        # First pass: Mark 'green' letters.
        for i, letter in enumerate(guess):
            if candidate[i] == letter:
                feedback[i] = 'green'
                candidate_letters[i] = None  # Mark this letter as used.

        # Second pass: Mark 'yellow' and 'grey'.
        for i, letter in enumerate(guess):
            if feedback[i] is None:  # Only consider letters not marked 'green'.
                if letter in candidate_letters:
                    feedback[i] = 'yellow'
                    # Remove the letter from candidate_letters after matching to prevent double-counting.
                    candidate_letters[candidate_letters.index(letter)] = None
                else:
                    feedback[i] = 'grey'

        return tuple(feedback)
    def __str__(self):
        return "Bayesian"