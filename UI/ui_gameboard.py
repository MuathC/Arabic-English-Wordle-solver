from PyQt6.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QLabel, QGridLayout,QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class GameBoard(QWidget):
    def __init__(self, title, language = "en"):
        super().__init__()
        self.title = title
        self.language = language
        self.init_ui()

    def init_ui(self):
        # check for language left right or vise versa.
        if self.language == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setFont(QFont("Noto Naskh Arabic", 14))
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.setFont(QFont("Arial", 12))

        layout = QVBoxLayout()
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Game board grid (6 rows x 5 columns, like Wordle)
        self.grid_widget = QWidget()

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setHorizontalSpacing(10)
        self.grid_layout.setVerticalSpacing(10)

        # Force grid layout direction to LTR even in RTL app
        if self.language == "ar":
            self.grid_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft) #VERY IMPORTANT

        # Create 6x5 grid of QLabel cells
        self.cells={}
        for row in range(6):
            for col in range(5):
                cell = QLabel("")
                cell.setMinimumSize(50, 50)
                cell.setMaximumSize(70, 70)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
                cell.setStyleSheet("""
                    background-color: #121213;
                    color: #d7dadc;
                    border: 2px solid #3a3a3c;
                    border-radius: 5px;
                """)
                self.grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell

        # Apply the layout to the grid widget
        self.grid_widget.setLayout(self.grid_layout)
        layout.addWidget(self.grid_widget)

        self.setLayout(layout)
       

        self.setLayout(layout)

    def update_cell(self, row, col, letter, color):
        cell = self.cells.get((row, col))
        if cell:
            cell.setText(letter)
            if color == "green":
                cell.setStyleSheet("""
                    background-color: #6aaa64;
                    color: white;
                    border: 2px solid #6aaa64;
                    border-radius: 5px;
                """)
            elif color == "yellow":
                cell.setStyleSheet("""
                    background-color: #c9b458;
                    color: white;
                    border: 2px solid #c9b458;
                    border-radius: 5px;
                """)
            elif color == "grey":
                cell.setStyleSheet("""
                    background-color: #787c7e;
                    color: white;
                    border: 2px solid #787c7e;
                    border-radius: 5px;
                """)
            else:
                cell.setStyleSheet("""
                    background-color: #121213;
                    color: #d7dadc;
                    border: 2px solid #3a3a3c;
                    border-radius: 5px;
                """)

    
    def clear_board(self):
        """
        Clears the board by resetting all cells.
        """
        for cell in self.cells.values():
            cell.setText("")
            cell.setStyleSheet("""
                background-color: #121213;
                color: #d7dadc;
                border: 2px solid #3a3a3c;
                border-radius: 5px;
            """)
        self.grid_layout.update()
        self.grid_layout.activate()
            
            
            

class KeyboardWidget(QWidget):
    def __init__(self,language):
        super().__init__()
        self.language = language
        self.letters = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(3)  # Reduced vertical spacing between rows
        layout.setContentsMargins(2, 2, 2, 2)  # Small padding around keyboard
        self.setLayout(layout)

        keyboard_map = {"en":["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"],
                        "ar":["أدجحخهعغفقثصض","طكمنتالبيسش","ظزوةىآرؤءئ"]
                        }
        
        key_rows = keyboard_map[self.language]
        for row_keys in key_rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)  # Tight horizontal spacing
            row_layout.addStretch()  # Push keys to center
            
            for char in row_keys:
                btn = QLabel(char)
                btn.setFixedSize(32, 42)  # Slightly larger keys
                btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
                btn.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))  # Bigger font
                btn.setStyleSheet("""
                    background-color: #818384;
                    color: white;
                    border-radius: 4px;
                """)
                self.letters[char] = btn
                row_layout.addWidget(btn)
            
            row_layout.addStretch()  # Push keys to center
            layout.addLayout(row_layout)

    def mark_letter_grey(self, letter):
        label = self.letters.get(letter.upper())
        if label:
            current_color = label.styleSheet()
            # Update to check for current keyboard color (#818384)
            if "background-color: #818384" in current_color:
                label.setStyleSheet("""
                    background-color: #3a3a3c;  
                    color: white;
                    border-radius: 4px;
                """)
                
    def mark_letter_yellow(self, letter):
        label = self.letters.get(letter.upper())
        if label:
            current_style = label.styleSheet()
            # Only upgrade to yellow if not already green
            if "#6aaa64" not in current_style:
                label.setStyleSheet("""
                    background-color: #c9b458;
                    color: white;
                    border-radius: 4px;
                """)
                
    def mark_letter_green(self, letter):
        label = self.letters.get(letter.upper())
        if label:
            # Always upgrade to green regardless of current state
            label.setStyleSheet("""
                background-color: #6aaa64;
                color: white;
                border-radius: 4px;
            """)

    def reset_keys(self):
        for label in self.letters.values():
            label.setStyleSheet("""
                background-color: #818384;  
                color: white;  
                border-radius: 4px;
            """)
