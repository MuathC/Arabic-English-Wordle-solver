from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QSizePolicy, QLabel, QLineEdit,QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer,QPropertyAnimation
from PyQt6.QtGui import QFont,QKeySequence,QShortcut

from env.ai_solver import AISolverThread
from UI.ui_gameboard import GameBoard
from env.wordle_env import WordleEnv
from agents.frequency_agent import FrequencyAgent
from agents.CSP_agent import CSP_agent
from agents.entropy_agent import EntropyAgent
from agents.bayesian_agent import BayesianAgent

from UI.translations import translations,get_translation_key
from UI.ui_helper import get_language_ui_config
from utils.word_processing.validation import is_valid_word
from data.config import ERROR_WORDS
class ComparisonWindow(QMainWindow):
    def __init__(self,language):
        """
        Expects four AI agent classes. Instances are created for each agent.
        """
        super().__init__()
        self.env = WordleEnv(language=language)
        self.language = language
        self.translate = translations[self.language]
        self.secret_word = self.env.generate_random_word()
        self.agents = [FrequencyAgent(language=language),EntropyAgent(language=language),BayesianAgent(language=language),CSP_agent(language=language)]
        self.ai_threads = []  # To hold solver threads for each agent
        self.boards = []  # To hold the four game boards
        self.init_ui()

    def init_ui(self):
        config = get_language_ui_config(self.language)
        self.setLayoutDirection(config["layout_direction"])
        self.setFont(config["font"])

        # Main container widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setStyleSheet("background-color: #121213; color: #d7dadc;")
        
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        # --- Top bar layout with back button ---
        top_layout = QHBoxLayout()
        self.back_btn = QPushButton(self.translate["back"])
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
        top_layout.addWidget(self.back_btn)
        top_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.addLayout(top_layout)

        # --- Word Selection Prompt ---
        self.word_prompt_widget = QWidget()
        prompt_layout = QVBoxLayout(self.word_prompt_widget)

        # Title label for the word selection
        prompt_label = QLabel(self.translate["choose_secret"])
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        prompt_layout.addWidget(prompt_label)

        # Buttons for word entry and random generation
        buttons_layout = QHBoxLayout()
        self.enter_word_btn = QPushButton(self.translate["enter_word_btn"])
        self.random_word_btn = QPushButton(self.translate["random_word_btn"])
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
        

        # Input field for a user-provided word (hidden by default)
        self.word_input = QLineEdit()
        self.word_input.setMaxLength(5)
        self.word_input.setPlaceholderText(self.translate["enter_word_prompt"])
        self.word_input.setFont(QFont("Helvetica", 16))
        self.word_input.hide()
        prompt_layout.addWidget(self.word_input)

        # Submit button for the entered word (hidden by default)
        self.word_submit_btn = QPushButton(self.translate["submit"])
        self.word_submit_btn.setStyleSheet(btn_style)
        self.word_submit_btn.hide()
        prompt_layout.addWidget(self.word_submit_btn)

        self.main_layout.addWidget(self.word_prompt_widget)

        # Connect the word selection buttons to their functions
        self.enter_word_btn.clicked.connect(self.prompt_for_word)
        self.word_submit_btn.clicked.connect(self.handle_word_submission)
        self.word_input.returnPressed.connect(self.word_submit_btn.click)
        self.random_word_btn.clicked.connect(self.handle_random_word)

        # --- Container for AI Board Comparison and Controls ---
        self.compare_ui_container = QWidget()
        compare_layout = QVBoxLayout(self.compare_ui_container)
        # Create a horizontal layout for four boards
        boards_layout = QHBoxLayout()
        # Initialize four GameBoard widgets (one for each agent)
        for idx, agent in enumerate(self.agents):
            board = GameBoard(f"Agent {idx + 1}",language=self.language)
            boards_layout.addWidget(board)
            self.boards.append(board)
        compare_layout.addLayout(boards_layout)
        self.compare_ui_container.hide()  # Hidden until word selection is complete

        self.main_layout.addWidget(self.compare_ui_container)

        # Set pointing hand cursor for interactive buttons
        for btn in [self.back_btn, self.enter_word_btn, self.random_word_btn, self.word_submit_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(config["font"])
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close)
        
          
        
    def keyPressEvent(self, event):
        # Allow ESC key to act like a back button click
        if event.key() == Qt.Key.Key_Escape:
            self.back_btn.click()
        super().keyPressEvent(event)

    def __get_title_label(self, board: GameBoard):
        """Utility: returns the title label widget from a GameBoard's layout."""
        title_label = board.layout().itemAt(0).widget()
        return title_label if isinstance(title_label, QLabel) else None

    def __set_title_label(self, board: GameBoard, label_text: str):
        """Utility: sets the title label text of a given board."""
        title_label = self.__get_title_label(board)
        if title_label:
            title_label.setText(label_text)

    def __show_temp_message(self, message):
        """Displays a temporary centered message for 1 second."""
        msg_label = QLabel(message, self)
        msg_label.setStyleSheet(
            "background-color: white; color: black; font-size: 16px; font-weight: bold; "
            "border-radius: 15px; padding: 10px;"
        )
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.adjustSize()

        # Center the message on the window
        screen_width = self.width()
        screen_height = self.height()
        label_width = msg_label.width() + 20
        label_height = msg_label.height() + 10
        msg_label.setFixedSize(label_width, label_height)
        msg_label.move((screen_width - label_width) // 2, (screen_height - label_height) // 2)
        msg_label.show()

        QTimer.singleShot(1000, msg_label.hide)

    def prompt_for_word(self):
        """Shows the input field and submit button when 'Enter 5-letter Word' is clicked."""
        self.word_input.show()
        self.word_submit_btn.show()
        self.word_input.setFocus()

    def handle_word_submission(self):
        """
        Validates the entered word and, if valid, uses it as the secret word.
        Also sets the titles for the comparison boards.
        """
        word = self.word_input.text().lower()
        if len(word) < 5:
            self.__show_temp_message(self.translate["not_enough_letters"])
            self.word_input.clear()
            return

        elif word not in self.agents[0].candidates:
            if is_valid_word(word):
                for agent in self.agents:
                    agent.candidates.append(word)
            else:
                ERROR_WORDS.append(word)
                self.__show_temp_message(self.translate["not_in_word_list"])
                self.word_input.clear()
                return


        self.secret_word = word
        # Update board titles for each agent before starting the AI solver threads
        for idx, agent in enumerate(self.agents):
            title =  self.translate["agent_title"].format(agent_name = self.translate[get_translation_key(str(agent))]) + "\n\n" + self.translate["word"] + ": " + self.secret_word.upper()
            self.__set_title_label(self.boards[idx], title)
        self.start_test_mode()

    def handle_random_word(self):
        """Generates a random word and uses it for all boards."""
        self.secret_word = self.env.generate_random_word()
        for idx, agent in enumerate(self.agents):
            title = self.translate["agent_title"].format(agent_name = self.translate[get_translation_key(str(agent))]) + "\n\n" + self.translate["word"] + ": " + self.secret_word.upper()
            self.__set_title_label(self.boards[idx], title)
        self.start_test_mode()

    def start_test_mode(self):
        """
        Hides the word selection UI, shows the comparison UI with four boards,
        and starts the AI solver threads for each agent.
        """
        self.word_prompt_widget.hide()
        self.compare_ui_container.show()
        self.start_all_ai_solvers()

    def start_all_ai_solvers(self):
        """
        Starts an AISolverThread for each agent and connects their signals to the corresponding board.
        """
        # Clear any previous threads if needed
        self.ai_threads = []
        for idx, agent in enumerate(self.agents):
            # Create a solver thread for each agent with the selected secret word
            ai_thread = AISolverThread(agent, self.secret_word,self.language)
            # Connect update signals with a lambda capturing the board index
            ai_thread.update_signal.connect(lambda row, col, letter, color, idx=idx:
                                            self.handle_ai_update(idx, row, col, letter, color))
            ai_thread.finished.connect(lambda idx=idx, thread=ai_thread:
                                       self.handle_ai_finished(idx, thread))
            self.ai_threads.append(ai_thread)
            ai_thread.start()

    def handle_ai_update(self, board_index, row, col, letter, color):
        """Updates the cell in the board corresponding to board_index."""
        self.boards[board_index].update_cell(row, col, letter.upper(), color)

    def handle_ai_finished(self, board_index, ai_thread):
        """
        Once an agent's AI solver thread finishes, append the result
        (Correct or Wrong) to the corresponding board's title.
        """
        last_guess = ai_thread.env.guesses[-1]
        secret_word = ai_thread.env.secret_word
        title_label = self.__get_title_label(self.boards[board_index])
        current_title = title_label.text() if title_label else ""

        if last_guess == secret_word:
            updated_title = current_title + "\n\n" + self.translate["correct"]
        else:
            updated_title = current_title + "\n\n" + self.translate["wrong"]
        self.__set_title_label(self.boards[board_index], updated_title)

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
