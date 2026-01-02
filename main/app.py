import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication
from UI.ui_start import StartPage
from data.config import ERROR_WORDS,words_to_add_path
from utils.file_processing import save_word_list,load_word_list
from utils.word_processing.validation import __is_english_alphabet

def on_exit():
    old = load_word_list(words_to_add_path)
    arabic_err = [word for word in ERROR_WORDS if not __is_english_alphabet(word) and word not in old]
    save_word_list(words_to_add_path,arabic_err,'a')
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.instance().aboutToQuit.connect(on_exit)
    start_page = StartPage()
    start_page.showMaximized()
    sys.exit(app.exec())
   
