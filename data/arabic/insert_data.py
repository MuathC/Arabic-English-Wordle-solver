import sys
import os

# Add the parent directory of the project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.file_processing import save_word_list, load_word_list
from data.config import all_words_arabic_path, words_to_add_path

new = load_word_list(words_to_add_path)
current = load_word_list(all_words_arabic_path)

for word in new:
    if len(word) == 5 and word not in current:
        current.append(word)

current.sort()
save_word_list(all_words_arabic_path, current)
save_word_list(words_to_add_path, [])