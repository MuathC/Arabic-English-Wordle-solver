
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QSizePolicy, QLabel, QLineEdit,QGraphicsOpacityEffect
)
from PyQt6.QtCore import  Qt,QTimer,QPropertyAnimation
from PyQt6.QtGui import QFont,QShortcut,QKeySequence

from env.ai_solver import AISolverThread
from UI.ui_gameboard import GameBoard
from env.wordle_env import WordleEnv
from data.config import ERROR_WORDS
from utils.word_processing.validation import is_valid_word
from UI.translations import translations,get_translation_key
from UI.ui_helper import get_language_ui_config

class TestWindow(QMainWindow):
    def __init__(self, selected_agent, language):
        super().__init__()
        self.language = language
        self.env = WordleEnv(language=language)
        self.agent = selected_agent(language=language)
        self.translate = translations[self.language]
        self.init_ui()

    def init_ui(self):
        # check for language left right or vise versa.
        config = get_language_ui_config(self.language)
        
        self.setLayoutDirection(config["layout_direction"])
        self.setFont(config["font"])

        # Main container widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #121213; color: #d7dadc;")

        # Back button at the top-right
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton(translations[self.language]["back"])
        self.back_btn.setStyleSheet("""
             QPushButton {
                background-color: #538d4e;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6faa64;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_btn)
        back_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.addLayout(back_layout)

        # Create a container for the word selection prompt
        self.word_prompt_widget = QWidget()
        prompt_layout = QVBoxLayout()
        self.word_prompt_widget.setLayout(prompt_layout)

        # Title label for word selection
        prompt_label = QLabel(translations[self.language]["choose_secret"])
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        prompt_layout.addWidget(prompt_label)

        # Two buttons: one for entering a word and one for generating one randomly
        buttons_layout = QHBoxLayout()
        self.enter_word_btn = QPushButton(translations[self.language]["enter_word_btn"])
        self.random_word_btn = QPushButton(translations[self.language]["random_word_btn"])
        btn_style = """
             QPushButton {
                background-color: #538d4e;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6faa64;
            }
        """
        self.enter_word_btn.setStyleSheet(btn_style)
        self.random_word_btn.setStyleSheet(btn_style)
        buttons_layout.addWidget(self.enter_word_btn)
        buttons_layout.addWidget(self.random_word_btn)
        prompt_layout.addLayout(buttons_layout)

        # Input field for user-provided word (hidden by default)
        self.word_input = QLineEdit()
        self.word_input.setMaxLength(5)
        self.word_input.setPlaceholderText(self.translate["enter_word_prompt"])
        self.word_input.setFont(QFont("Helvetica", 16))
        self.word_input.hide()
        prompt_layout.addWidget(self.word_input)

        # A submit button for the entered word (hidden by default)
        self.word_submit_btn = QPushButton(self.translate["submit"])
        self.word_submit_btn.setStyleSheet(btn_style)
        self.word_submit_btn.hide()
        prompt_layout.addWidget(self.word_submit_btn)

        # Add the word prompt container to the main layout
        self.main_layout.addWidget(self.word_prompt_widget)

        # Connect the buttons to their functions
        self.enter_word_btn.clicked.connect(self.prompt_for_word)
        self.word_submit_btn.clicked.connect(self.handle_word_submission)
        self.word_input.returnPressed.connect(self.word_submit_btn.click)
        self.random_word_btn.clicked.connect(self.handle_random_word)

        # Container for the AI board & restart controls (hidden until word selection)
        self.test_ui_container = QWidget()
        test_layout = QVBoxLayout()
        self.test_ui_container.setLayout(test_layout)
        self.test_ui_container.hide()  # will be shown after word selection

        # AI Board
        self.ai_board = GameBoard("AI Agent",language=self.language)
        test_layout.addWidget(self.ai_board)

        # Add the test UI container to the main layout
        self.main_layout.addWidget(self.test_ui_container)
        for btn in [self.back_btn, self.enter_word_btn, self.random_word_btn, self.word_submit_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(config["font"])
        
        close_app_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_app_shortcut.activated.connect(self.close)
        
    
    
   
        
   
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.back_btn.click()  # Simulate back button click
        super().keyPressEvent(event)
    
    def __get_title_label(self):
        title_label = self.ai_board.layout().itemAt(0).widget()
        if isinstance(title_label, QLabel):
            return title_label
        
        else:
            return None
        
    def __set_title_label(self,label):
        title_label = self.__get_title_label()
        if isinstance(title_label, QLabel):
            title_label.setText(label)
        
    def __show_temp_message(self, message):
        """Displays a temporary message in a rounded rectangle for 2 seconds."""
        self.msg_label = QLabel(message, self)
        self.msg_label.setStyleSheet(
            "background-color: white; color: black; font-size: 16px; font-weight: bold; "
            "border-radius: 15px; padding: 10px;"
        )
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.adjustSize()

        # Centering the label
        screen_width = self.width()
        screen_height = self.height()
        label_width = self.msg_label.width() + 20  # Add extra width for padding
        label_height = self.msg_label.height() + 10  # Add extra height for padding
        self.msg_label.setFixedSize(label_width, label_height)
        self.msg_label.move((screen_width - label_width) // 2, (screen_height - label_height) // 2)

        self.msg_label.show()

        # Hide the message after 2 seconds
        QTimer.singleShot(1000, self.msg_label.hide)
        
    
    def prompt_for_word(self):
        """
        Called when user clicks 'Enter 5-letter Word'.
        Shows the input field and submit button.
        """

        self.word_input.show()
        self.word_submit_btn.show()
        self.word_input.setFocus()

    def handle_word_submission(self):
        """
        Called when user submits a word.
        Validates the input and then uses it as the secret word.
        """
        word = self.word_input.text()
        word = word.lower()
        if len(word) < 5:
            self.__show_temp_message(self.translate["not_enough_letters"])
            self.word_input.clear()
            return

        elif word not in self.agent.candidates:
            if is_valid_word(word):
                self.agent.candidates.append(word)
            else:
                ERROR_WORDS.append(word)
                self.__show_temp_message(self.translate["not_in_word_list"])
                self.word_input.clear()
                return
        
        self.secret_word = word
        
            
        self.__set_title_label(self.translate["agent_title"].format(agent_name = self.translate[get_translation_key(str(self.agent))]) + "\n\n" + self.translate["word"] + ": " + self.secret_word.upper())
        
        self.start_test_mode()

    def handle_random_word(self):
        """
        Called when user chooses to generate a random word.
        """
        self.secret_word= self.env.generate_random_word()
        
        self.__set_title_label(self.translate["agent_title"].format(agent_name = self.translate[get_translation_key(str(self.agent))]) + "\n\n" + self.translate["word"] + ": " + self.secret_word.upper())
        self.start_test_mode()

    def start_test_mode(self):
        """
        Hides the word prompt UI and shows the AI board UI.
        Starts the AI solver process.
        """
        # Hide the word selection prompt
        self.word_prompt_widget.hide()
        # Show the test UI container with the AI board
        self.test_ui_container.show()
        # Start the AI solver process
        self.start_ai_solver()

    def fade_in_widget(self,widget,on_finished = None):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(400)
        animation.setStartValue(0)
        animation.setEndValue(1)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        widget.animation = animation
        
   
    def go_back(self):
        
        self.start_page.showMaximized()

        # Fade in the start page after a short delay to allow the fade-out transition to finish
        def on_fade_finished():
            self.close()

        self.fade_in_widget(self.start_page, on_fade_finished)
        

    
        
    def start_ai_solver(self):
        #print(f"agent: {self.agent}, word: {self.secret_word}" )
        self.ai_thread = AISolverThread(self.agent, self.secret_word,self.language)
        self.ai_thread.update_signal.connect(self.handle_ai_update)
        self.ai_thread.finished.connect(self.handle_ai_finished)
        self.ai_thread.start()

    def handle_ai_update(self, row, col, letter, color):
        self.ai_board.update_cell(row, col, letter.upper(), color)

    def handle_ai_finished(self):
        last_guess = self.ai_thread.env.guesses[-1]
        secret_word = self.ai_thread.env.secret_word
        current_title = self.__get_title_label().text()
        
        if last_guess == secret_word:
            self.__set_title_label(current_title + "\n\n" + self.translate["correct"])
            
        else:
            self.__set_title_label(current_title + "\n\n" + self.translate["wrong"])
            
