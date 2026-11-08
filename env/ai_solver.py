import time

from PyQt6.QtCore import QThread, pyqtSignal

from env.wordle_env import WordleEnv


class AISolverThread(QThread):
    """Plays one game with an agent off the UI thread, emitting each tile as it is revealed."""

    update_signal = pyqtSignal(int, int, str, str)  # row, col, letter, color

    def __init__(self, agent, secret_word, language="en", tile_delay=0.08):
        super().__init__()
        self.agent = agent
        self.env = WordleEnv(language=language)
        self.env.reset(secret_word)
        self.tile_delay = tile_delay
        self.is_ran = False
        self._stopped = False

    def run(self):
        self.agent.reset()
        while not self.env.game_over and not self._stopped:
            guess = self.agent.get_guess()
            if guess is None:  # no candidate fits the feedback any more
                break
            row = self.env.guess_count
            feedback = self.env.guess(guess)
            for col, (letter, color) in enumerate(zip(guess, feedback)):
                if self._stopped:
                    return
                self.update_signal.emit(row, col, letter, color)
                time.sleep(self.tile_delay)
            self.agent.update(guess, feedback)
        self.is_ran = not self._stopped

    def stop(self):
        self._stopped = True
        self.wait()
