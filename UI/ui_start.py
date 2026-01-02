from PyQt6.QtWidgets import QMainWindow,QMenu, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from agents.CSP_agent import CSP_agent
from agents.bayesian_agent import BayesianAgent
from agents.frequency_agent import FrequencyAgent
from agents.entropy_agent import EntropyAgent
from UI.ui_comparison import ComparisonWindow
from UI.ui_mainwindow import MainWindow
from UI.ui_testwindow import TestWindow
from UI.translations import translations,get_translation_key
from UI.ui_helper import get_language_ui_config

class StartPage(QMainWindow):
    def __init__(self,language="en"):
        super().__init__()
        self.language = language
        self.translate = translations[language]
        self.setWindowTitle(self.translate["window_title"])
        self.selected_agent = None
        self.init_ui()
        

    def init_ui(self):
        # Gradient theme and modern color scheme
        config = get_language_ui_config(self.language)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121213;
            }
            QWidget {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #121213, stop:1 #1f1f23
                );
                color: #d7dadc;
            }
        """)
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("border: none;")
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        self.central_widget.setLayout(self.layout)
        
        self.language_menu_btn = QPushButton("🌐   " + ("English       ▼" if self.language == "en" else "العربية         ▼"))
        self.language_menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_menu_btn.setFixedWidth(120)
        self.language_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3c;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #505053;  /* Lighter on hover */
            }
            QPushButton::menu-indicator {
                image: none;  /* Hides default arrow */
            }
        """)        

        language_menu = QMenu()
        english_action = language_menu.addAction("English")
        arabic_action = language_menu.addAction("العربية")
        self.language_menu_btn.setMenu(language_menu)

        # Connect actions
        english_action.triggered.connect(lambda: self.restart_with_language("en"))
        arabic_action.triggered.connect(lambda: self.restart_with_language("ar"))

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(self.language_menu_btn)
        lang_layout.addStretch()
        self.layout.addLayout(lang_layout)
        # Title
        title_label = QLabel(translations[self.language]["title"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Helvetica", 48, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #d7dadc;")
        self.layout.addWidget(title_label)

        subtitle_label = QLabel(translations[self.language]["subtitle"])
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Helvetica", 22))
        subtitle_label.setStyleSheet("color: #a4a5a8;")
        self.layout.addWidget(subtitle_label)

        # Agent Selection
        self.agent_label = QLabel(translations[self.language]["choose_agent"])
        self.agent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.agent_label.setFont(QFont("Helvetica", 16))
        self.agent_label.setStyleSheet("margin-top: 20px;")
        self.layout.addWidget(self.agent_label)

        agent_buttons_layout = QHBoxLayout()
        self.CSP_btn = QPushButton(translations[self.language]["agent_CSP"])
        self.Bayesian_btn = QPushButton(translations[self.language]["agent_Bayesian"])
        self.Frequency_btn = QPushButton(translations[self.language]["agent_Frequency"])
        self.Entropy_btn = QPushButton(translations[self.language]["agent_Entropy"])
        self.agent_buttons = [self.CSP_btn, self.Bayesian_btn, self.Frequency_btn, self.Entropy_btn]

        button_style = """
            QPushButton {
                background-color: #538d4e;
                color: white;
                padding: 15px 20px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #6faa64;
            }
        """
        for btn in self.agent_buttons:
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(config["font"])
            agent_buttons_layout.addWidget(btn)
        self.layout.addLayout(agent_buttons_layout)

        # Mode Selection (Initially Hidden)
        self.mode_label = QLabel(self.translate["select_mode"])
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setFont(QFont("Helvetica", 16))
        self.mode_label.setStyleSheet("margin-top: 30px;")
        self.mode_label.hide()
        self.layout.addWidget(self.mode_label)
        

        mode_buttons_layout = QHBoxLayout()
        self.test_btn = QPushButton(self.translate["mode_test"])
        self.play_btn = QPushButton(self.translate["mode_play"])
        self.comparison_btn = QPushButton(self.translate["mode_comparison"])
        self.mode_buttons = [self.test_btn, self.play_btn, self.comparison_btn]

        for btn in self.mode_buttons:
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(config["font"])
            btn.hide()
            mode_buttons_layout.addWidget(btn)

        self.layout.addLayout(mode_buttons_layout)

        # Quit Button
        self.quit_btn = QPushButton(self.translate["quit"])
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 15px 20px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_btn.setFont(config["font"])
        self.quit_btn.clicked.connect(self.close)
        self.layout.addWidget(self.quit_btn)

        # Connect Mode Buttons
        self.CSP_btn.clicked.connect(lambda: self.select_agent("CSP"))
        self.Bayesian_btn.clicked.connect(lambda: self.select_agent("Bayesian"))
        self.Frequency_btn.clicked.connect(lambda: self.select_agent("Frequency"))
        self.Entropy_btn.clicked.connect(lambda: self.select_agent("Entropy"))
        self.test_btn.clicked.connect(self.launch_test_mode)
        self.play_btn.clicked.connect(self.launch_play_mode)
        self.comparison_btn.clicked.connect(self.launch_comparison_mode)
        self.select_agent("CSP")

        # Shortcut to close window
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close)
        
    def restart_with_language(self, new_language):
        if new_language == self.language:
            return

        # Create a frameless loading popup with rounded corners
        loading_dialog = QDialog(self)
        loading_dialog.setWindowTitle("")
        loading_dialog.setModal(True)
        loading_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        loading_dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Outer layout to give padding and soft border effect
        outer_layout = QVBoxLayout(loading_dialog)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # Inner widget to apply rounded corners and background
        inner_widget = QLabel(self.translate["wait"])
        inner_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_widget.setStyleSheet("""
            background-color: #2c2c2e;
            color: white;
            padding: 20px;
            border-radius: 12px;
            font-size: 14pt;
        """)

        outer_layout.addWidget(inner_widget)

        # Center and show the dialog
        loading_dialog.setFixedSize(220, 100)
        loading_dialog.move(self.geometry().center() - loading_dialog.rect().center())
        loading_dialog.show()

        # Delay and then switch language
        QTimer.singleShot(300, lambda: self._perform_language_restart(new_language, loading_dialog))

    def _perform_language_restart(self, new_language, dialog):
        dialog.accept()
        self.close()
        self.new_window = StartPage(language=new_language)
        self.new_window.showMaximized()
       

        

    def fade_in_widget(self, widget, on_finished=None):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(100)
        animation.setStartValue(0)
        animation.setEndValue(1)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        widget.animation = animation

    
        

    def show_window(self, window):
        
        window.showMaximized()


    def show_loading_dialog(self, message="Loading..."):
        loading_dialog = QDialog(self)
        loading_dialog.setModal(True)
        loading_dialog.setWindowTitle(message)
        loading_dialog.setStyleSheet("background-color: #1f1f23; color: white;")
        layout = QVBoxLayout()

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        loading_dialog.setLayout(layout)
        loading_dialog.setFixedSize(300, 100)
        return loading_dialog

    def select_agent(self, agent_name):
        self.selected_agent = agent_name
        self.agent_label.setText(self.translate["selected"] + ": " + self.translate[get_translation_key(self.selected_agent)])
        self.mode_label.show()
        for btn in self.mode_buttons:
            btn.show()

    def launch_test_mode(self):
        self.loading_dialog = None  # Placeholder for the dialog
        self.loading_timer = QTimer(self)
        self.loading_timer.setSingleShot(True)

        def show_loading():
            self.loading_dialog = self.show_loading_dialog("Launching Test Mode...")
            self.loading_dialog.show()
            QApplication.processEvents()

        self.loading_timer.timeout.connect(show_loading)
        self.loading_timer.start(500)  # Show loading dialog only if it takes longer than 300ms

        def load_and_transition():
            self.test_window = TestWindow(self.string_to_agent(self.selected_agent),language=self.language)
            self.test_window.start_page = self
            self.test_window.setWindowTitle(self.translate["window_title_test"].format(agent = self.translate[get_translation_key(self.selected_agent)]))
            self.show_window(self.test_window)
            def on_fade_finished():
                if self.loading_dialog:
                    self.loading_dialog.accept()
                self.hide()

            self.fade_in_widget(self.test_window, on_finished=on_fade_finished)
            self.loading_timer.stop()  # Stop the timer if it's still counting

        QTimer.singleShot(0, load_and_transition)

    def launch_play_mode(self):
        self.loading_dialog = None
        self.loading_timer = QTimer(self)
        self.loading_timer.setSingleShot(True)

        def show_loading():
            self.loading_dialog = self.show_loading_dialog("Launching Play Mode...")
            self.loading_dialog.show()
            QApplication.processEvents()

        self.loading_timer.timeout.connect(show_loading)
        self.loading_timer.start(500)

        def load_and_transition():
            self.main_window = MainWindow(self.string_to_agent(self.selected_agent),language=self.language)
            self.main_window.setWindowTitle(self.translate["window_title_play"].format(agent = self.translate[get_translation_key(self.selected_agent)]))
            self.main_window.start_page = self
            self.main_window.is_play_mode = True
            self.main_window.env.reset()

            self.show_window(self.main_window)

            def on_fade_finished():
                if self.loading_dialog:
                    self.loading_dialog.accept()
                self.hide()

            self.fade_in_widget(self.main_window, on_finished=on_fade_finished)
            self.loading_timer.stop()

        QTimer.singleShot(0, load_and_transition)

    def launch_comparison_mode(self):
        self.loading_dialog = None
        self.loading_timer = QTimer(self)
        self.loading_timer.setSingleShot(True)

        def show_loading():
            self.loading_dialog = self.show_loading_dialog("Launching Comparison...")
            self.loading_dialog.show()
            QApplication.processEvents()

        self.loading_timer.timeout.connect(show_loading)
        self.loading_timer.start(500)

        def load_and_transition():
            self.comparison_window = ComparisonWindow(language=self.language)
            self.comparison_window.setWindowTitle(self.translate["window_title_comp"])
            self.comparison_window.start_page = self
            self.show_window(self.comparison_window)

            def on_fade_finished():
                if self.loading_dialog:
                    self.loading_dialog.accept()
                self.hide()

            self.fade_in_widget(self.comparison_window, on_finished=on_fade_finished)
            self.loading_timer.stop()

        QTimer.singleShot(0, load_and_transition)

    def string_to_agent(self, agent_name):
        if agent_name == "Frequency":
            return FrequencyAgent
        elif agent_name == "Bayesian":
            return BayesianAgent
        elif agent_name == "CSP":
            return CSP_agent
        elif agent_name == "Entropy":
            return EntropyAgent
