import os
import json
import math

from agents.base_agent import BaseAgent
from data.config import ALL_WORDS_ENGLISH
from tqdm import tqdm
from data.config import cache_path_en,cache_path_ar
class EntropyAgent(BaseAgent):
    def __init__(self, cache_filename=None,language="en"):
        """
        Initialize the EntropyAgent.

        Args:
            all_words (list): Full list of guessable words.
            valid_answers (list): List of valid answer words.
            cache_filename (str): Filename for storing cached entropy values.
        """
        super().__init__()
        self.language = language

        self.all_words = super().candidates(language=self.language)

        if cache_filename is None:
            if self.language == "en":
                self.cache_filename = cache_path_en
            elif self.language == "ar":
                self.cache_filename = cache_path_ar
            else:
                raise ValueError(f"Unsupported language: {self.language}")

        # This dictionary caches entropy values computed over the full valid_answers list.
        self.entropy_cache = {}
        self.previous_guesses = []
        # Initialize the candidate pool (the current set of valid answers).
        self.reset()
        # Precompute entropy values for the first move if cache is not loaded.
        self._load_or_compute_entropy_cache()

    def reset(self):
        """
        Reset the agent's state for a new game.
        This resets the candidate pool to the full set of valid answers.
        """
        self.candidates = list(self.all_words)
        self.previous_guesses = []


    def _load_or_compute_entropy_cache(self):
        """
        Loads the entropy cache from file if it exists; otherwise computes and caches it.
        Entropy here is computed over the full valid_answers list.
        """
        if os.path.exists(self.cache_filename):
            with open(self.cache_filename, "r") as f:
                self.entropy_cache = json.load(f)
        else:
            print(f"\nComputing entropy cache for language='{self.language}' ...\n")
            total_answers = len(self.all_words)

            # Initialize progress bar
            with tqdm(total=len(self.all_words), desc="Computing entropy", unit="word") as pbar:
                for guess in self.all_words:
                    feedback_counts = {}
                    for answer in self.all_words:
                        fb = self.compute_feedback(guess, answer)
                        feedback_counts[fb] = feedback_counts.get(fb, 0) + 1

                    # Compute entropy for this guess
                    entropy = 0.0
                    for count in feedback_counts.values():
                        p = count / total_answers
                        entropy -= p * math.log2(p)

                    self.entropy_cache[guess] = entropy
                    pbar.update(1)  # Update progress bar

            with open(self.cache_filename, "w", encoding="utf-8") as f:
                json.dump(self.entropy_cache, f)
            print("Entropy cache computed and saved.")

    

    def compute_feedback(self, guess, answer):
        """
        Compute Wordle-style feedback for a given guess and answer.
        Feedback is represented as a tuple of strings (e.g., ('green', 'grey', 'yellow', 'grey', 'green')).

        Uses a two-pass approach with a letter frequency count to correctly mark duplicates.

        Args:
            guess (str): The guessed word.
            answer (str): The actual answer word.

        Returns:
            tuple: The feedback for each letter.
        """
        feedback = [None] * len(guess)
        # Build frequency dictionary for letters in answer.
        answer_freq = {}
        for ch in answer:
            answer_freq[ch] = answer_freq.get(ch, 0) + 1

        # First pass: mark greens and reduce frequency.
        for i in range(len(guess)):
            if guess[i] == answer[i]:
                feedback[i] = 'green'
                answer_freq[guess[i]] -= 1

        # Second pass: mark yellows or greys.
        for i in range(len(guess)):
            if feedback[i] is None:
                if guess[i] in answer_freq and answer_freq[guess[i]] > 0:
                    feedback[i] = 'yellow'
                    answer_freq[guess[i]] -= 1
                else:
                    feedback[i] = 'grey'
        return tuple(feedback)

    def _compute_entropy_over_candidates(self):
        """
        Compute the entropy for each possible guess over the current candidate pool.
        This is used when the candidate pool is smaller than the full valid_answers.

        Returns:
            dict: A dictionary mapping guess words to their computed entropy.
        """
        entropy_dict = {}
        total_candidates = len(self.candidates)
        for guess in self.all_words:
            feedback_counts = {}
            for answer in self.candidates:
                fb = self.compute_feedback(guess, answer)
                feedback_counts[fb] = feedback_counts.get(fb, 0) + 1
            entropy = 0.0
            for count in feedback_counts.values():
                p = count / total_candidates
                entropy -= p * math.log2(p)
            entropy_dict[guess] = entropy
        return entropy_dict

    def get_guess(self):
        """
        Return the agent's next guess.
        If the candidate pool is full (start of game), use the precomputed entropy cache.
        Otherwise, compute the entropy values over the current candidate pool.
        If only one candidate remains, return it immediately.

        Returns:
            str: The guess with the highest entropy (i.e., expected information gain).
        """
        if len(self.candidates) == 1:
            return self.candidates[0]
        if set(self.candidates) == set(self.all_words):
            # Choose the word with maximum entropy from cache.
            best_guess = max(self.all_words, key=lambda word: self.entropy_cache.get(word, 0))
        else:
            entropy_dict = self._compute_entropy_over_candidates()
            best_guess = max(self.all_words, key=lambda word: entropy_dict.get(word, 0))
            
        self.previous_guesses.append(best_guess)
        return best_guess

    def update(self, guess, feedback):
        """
        Update the candidate pool based on the feedback from a guess.
        Only keep candidates that would produce the same feedback.
        """
        # Ensure the provided feedback is a tuple.
        if not isinstance(feedback, tuple):
            feedback = tuple(feedback)

        new_candidates = []
        for word in self.candidates:
            if word not in self.previous_guesses:
                computed_feedback = self.compute_feedback(guess, word)
                if computed_feedback == feedback:
                    new_candidates.append(word)
        self.candidates = new_candidates
        if len(self.candidates) == 0:
            print("ERROR: No candidates left! Something is wrong.")
    def __str__(self):
        return "Entropy"

