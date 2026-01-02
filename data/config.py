import os
from utils.file_processing import load_word_list

# Dynamically build the path to the all_words.txt file
current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of the current script
english_all_words_path = os.path.join(current_dir, '..', r'data\english', 'english_all_words.txt') 
english_game_words_path = os.path.join(current_dir, '..', r'data\english', 'english_game_words.txt')
all_words_arabic_path = os.path.join(current_dir, '..', r'data\arabic', 'arabic_words.txt')
words_to_add_path = os.path.join(current_dir, '..', r'data\arabic', 'words_to_add.txt')

cache_path_en = os.path.join(current_dir, '..', 'data', 'entropy_cache_en.json')
cache_path_ar = os.path.join(current_dir, '..', 'data', 'entropy_cache_ar.json')
# I changed path dont forget
ALL_WORDS_ENGLISH = load_word_list(english_all_words_path)
GAME_WORDS_ENGLISH = load_word_list(english_game_words_path)

ALL_WORDS_ARABIC = load_word_list(all_words_arabic_path)
ERROR_WORDS = []
