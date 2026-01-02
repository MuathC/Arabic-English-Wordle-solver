from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QLabel,QGraphicsOpacityEffect
)
from PyQt6.QtGui import QFont,QShortcut,QKeySequence
from PyQt6.QtCore import  Qt, QTimer,QPropertyAnimation

from env.ai_solver import AISolverThread
from UI.ui_gameboard import GameBoard,KeyboardWidget
from env.wordle_env import WordleEnv

from UI.translations import translations,get_translation_key
from UI.ui_helper import get_language_ui_config
from utils.word_processing.validation import is_valid_word
from data.config import ERROR_WORDS
class MainWindow(QMainWindow):
    def __init__(self,selected_agent , language):
        super().__init__()
        self.language = language
        self.env = WordleEnv(language= language)
        self.ai_thread = None
        self.current_player_row = 0
        self.agent = selected_agent(language = language)
        self.is_play_mode = False
        self.keyboard = KeyboardWidget(self.language)
        self.translate = translations[self.language]
        self.init_ui()
        

    
    def init_ui(self):
        # check for language left right or vise versa.
        config = get_language_ui_config(self.language)
        self.setLayoutDirection(config["layout_direction"])
        self.setFont(config["font"])

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setStyleSheet("background-color: #121213; color: #d7dadc;")

        # Back button layout
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton(self.translate["back"])
        back_btn_style = """
            QPushButton {
            background-color: #538d4e;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6faa64; /* Brighter green */
             }
            """
        self.back_btn.setStyleSheet(back_btn_style)
        self.back_btn.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_btn)
        back_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(back_layout)

        # Control panel
        control_layout = QHBoxLayout()
        self.reset_btn = QPushButton(self.translate["reset"])
        button_style = """
            QPushButton {
            background-color: #538d4e;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6faa64; /* Brighter green */
             }
            """
        self.reset_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.reset_btn)
        main_layout.addLayout(control_layout)

        # Split layout for player & AI
        split_layout = QHBoxLayout()
        self.player_board = GameBoard(self.translate["player"],language = self.language)
        self.ai_board = GameBoard(self.translate["agent_title"].format(agent_name=self.translate[get_translation_key(str(self.agent))]),language = self.language)
        split_layout.addWidget(self.player_board)
        split_layout.addWidget(self.ai_board)
        main_layout.addLayout(split_layout)

        # Player input
        input_layout = QHBoxLayout()
        self.guess_input = QLineEdit()
        self.guess_input.setMaxLength(5)
        if self.language == "ar":
            self.guess_input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.guess_input.setPlaceholderText(self.translate["enter_word_prompt"])
        self.guess_input.setFont(QFont("Amiri", 18))
        self.guess_input.setFocus()
        self.submit_btn = QPushButton(self.translate["submit"])
        self.submit_btn.setStyleSheet(button_style)


        input_layout.addWidget(self.guess_input)
        input_layout.addWidget(self.submit_btn)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.keyboard, stretch=0)  # Prevent vertical stretching
    
        

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Helvetica", 14))
        main_layout.addWidget(self.status_label)

        # Connect buttons
        self.reset_btn.clicked.connect(self.reset_boards)
        self.submit_btn.clicked.connect(self.submit_guess)
        self.guess_input.returnPressed.connect(self.submit_btn.click)
        self.guess_input.setFocus()
        btns = [self.back_btn, self.reset_btn, self.submit_btn]
        for btn in btns:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(config["font"])
        close_app_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_app_shortcut.activated.connect(self.close)
        
        reset_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reset_shortcut.activated.connect(self.reset_btn.click)
    
    
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
        
    
          
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.back_btn.click()  
        super().keyPressEvent(event)
        
        
    def go_back(self):
        self.start_page.showMaximized()

        # Fade in the start page after a short delay to allow the fade-out transition to finish
        def on_fade_finished():
            self.close()

        self.fade_in_widget(self.start_page, on_fade_finished)

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
        
    def reset_boards(self):
        self.env.reset()
        for board in [self.player_board, self.ai_board]:
            board.clear_board()
        self.guess_input.clear()
        self.guess_input.show()
        self.submit_btn.show()
        self.current_player_row = 0
        if self.ai_thread:
            self.ai_thread.stop()
        self.status_label.hide()
        self.guess_input.setFocus()
        self.keyboard.reset_keys()


    def submit_guess(self):
        guess = self.guess_input.text().lower()
        
        if len(guess) < 5:
            self.__show_temp_message(self.translate["not_enough_letters"])
            self.guess_input.clear()
            return

        elif guess not in self.agent.candidates:
            if is_valid_word(guess):
                self.agent.candidates.append(guess)
            else:
                ERROR_WORDS.append(guess)
                self.__show_temp_message(self.translate["not_in_word_list"])
                self.guess_input.clear()
                return
        
        self.status_label.setText("")
        feedback = self.env.guess(guess)
        for col, (letter, color) in enumerate(zip(guess, feedback)):
            self.player_board.update_cell(self.current_player_row, col, letter.upper(), color)
        
        for col, (letter, color) in enumerate(zip(guess, feedback)):
            if not self.is_play_mode:
                continue
            else:
                if color == "green":
                    self.keyboard.mark_letter_green(letter)
                elif color == "yellow":
                    self.keyboard.mark_letter_yellow(letter)
                elif color == "grey":
                    self.keyboard.mark_letter_grey(letter)
            
                
        self.current_player_row += 1
        self.guess_input.clear()

        if self.env.game_over:
            QTimer.singleShot(1000, self.start_ai_solver)
            self.guess_input.hide()
            self.submit_btn.hide()


    def start_ai_solver(self):
        self.ai_thread = AISolverThread(self.agent, self.env.secret_word,self.language)
        self.ai_thread.update_signal.connect(self.handle_ai_update)
        self.ai_thread.finished.connect(self.handle_ai_finished)
        self.ai_thread.start()
        
      
        

    def handle_ai_update(self, row, col, letter, color):
        self.ai_board.update_cell(row, col, letter.upper(), color)
        
    def handle_ai_finished(self):
        """This runs after AI finishes to update the status label."""
        if not self.is_play_mode or self.ai_thread is None or not self.ai_thread.is_ran or not self.ai_thread.env.game_over:
            return

        player_last_guess = self.env.guesses[-1]
        agent_last_guess = self.ai_thread.env.guesses[-1]
        secret_word = self.env.secret_word
        

        if player_last_guess == secret_word and agent_last_guess == secret_word:
            if self.env.guess_count > self.ai_thread.env.guess_count:
                result_text = self.translate["lose_fewer_attempts"]
            elif self.env.guess_count < self.ai_thread.env.guess_count:
                result_text = self.translate["win_fewer_attempts"]
            else:
                result_text = self.translate["draw_same_attempts"]

        elif player_last_guess != secret_word and agent_last_guess == secret_word:
            result_text = self.translate["lose_only_agent_guessed"].format(word=secret_word)

        elif player_last_guess == secret_word and agent_last_guess != secret_word:
            result_text = self.translate["win_only_player_guessed"]

        else:
            result_text = self.translate["draw_neither_guessed"].format(word=secret_word)

        self.status_label.setText(result_text)
        self.status_label.show()
