from typing import override
import enchant
from PySide6 import QtCore, QtWidgets, QtGui
import sys
import qdarktheme

my_dict = enchant.Dict('en_US')
added_words: list[str]  = ['aunty', 'leapt', 'aider', 'agora', 'leant', 'abled', 'gayly', 'golem', 'haute', 'fibre', 'pinky',
                           'briar', 'iliac', 'caddy', 'masse', 'donut', 'plier', 'snuck', 'octad', 'utile', 'ombre', 'flyer',
                           'loupe', 'rebar', 'ramen', 'ovine', 'sheik', 'crump', 'doula', 'chuff', 'folky', 'primo', 'eying',
                           'caput', 'petri', 'chica', 'droit', 'recut', 'carte', 'vaper', 'ungag', 'loofa', 'cyber', 'convo',
                           'kiddy', 'piler', 'rewax', 'panko', 'lacer', 'retag', 'annal', 'glute', 'pinot', 'aioli', 'laddy',
                           'unsee', 'paned', 'scape', 'penne', 'slyer', 'ebook', 'merch', 'stymy', 'acidy', 'ochre', 'lordy',
                           'femme', 'homie', 'hedgy', 'rager', 'smore', 'prima', 'ursid', 'anima', 'ortho', 'odour', 'apnea',
                           'melty', 'biome', 'niner', 'haram', 'whirr', 'sicky', 'stoma', 'unarm', 'bento', 'kefir', 'ichor',
                           'untax', 'smarm', 'tryer', 'aimer', 'hoser', 'outro', 'umami', 'repot', 'relit', 'moult', 'aglet',
                           'petit', 'inker', 'ricin', 'tufty']
remaining_letters: list[str]  = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
required_letters: list[str] = []
word_count = 1


class WordleHelper(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Wordle Helper')

        # Create grid for the widget
        grid_layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout(self)

        # Letter box widgets
        letters_layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        self.letters: list[LetterBox] = []

        for i in range(5):
            self.letters.append(LetterBox(i))
            _ = self.letters[i].change_focus.connect(self.focus_letter) # connect to slot for focusing a different letter
            letters_layout.addWidget(self.letters[i], 0, i + 1)

        # add spacing on either side
        letter_spacer_left: QtWidgets.QSpacerItem = QtWidgets.QSpacerItem(10, 0)
        letter_spacer_right: QtWidgets.QSpacerItem = QtWidgets.QSpacerItem(10, 0)
        letters_layout.addItem(letter_spacer_left, 0, 0)
        letters_layout.addItem(letter_spacer_right, 0, 6)

        letters_layout.setHorizontalSpacing(10) # add padding between letters
        letters_layout.setColumnStretch(0, 1) # let spacers consume extra space
        letters_layout.setColumnStretch(6, 1)
        grid_layout.addLayout(letters_layout, 0, 0)

        # Widgets for letters to not include
        self.exclude_label: QtWidgets.QLabel = QtWidgets.QLabel('Not in the word:')
        self.exclude_letters: InputBox = InputBox()

        grid_layout.addWidget(self.exclude_label, 1, 0)
        grid_layout.addWidget(self.exclude_letters, 2, 0)

        # Widgets for letter to include
        self.include_label: QtWidgets.QLabel = QtWidgets.QLabel('In the word somewhere:')
        self.include_letters: InputBox = InputBox()

        grid_layout.addWidget(self.include_label, 3, 0)
        grid_layout.addWidget(self.include_letters, 4, 0)

        # Widget for "Find Words" button
        self.find_button: QtWidgets.QPushButton = QtWidgets.QPushButton('Find Words')
        _ = self.find_button.clicked.connect(self.find_words)

        grid_layout.addWidget(self.find_button, 5, 0)

        # Add spacer to consume extra vertical space in first column
        spacer: QtWidgets.QSpacerItem = QtWidgets.QSpacerItem(10, 10, vData=QtWidgets.QSizePolicy.Policy.Ignored)
        grid_layout.addItem(spacer, 6, 0)

        # Widget for found words
        self.found_words: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        font: QtGui.QFont = QtGui.QFont('Monospace') # Use monospace font for the found words
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.found_words.setFont(font)
        self.found_words.setReadOnly(True)

        grid_layout.addWidget(self.found_words, 0, 1, 7, 1)

        # Add nice spacing
        grid_layout.setColumnStretch(0, 1) # First and second column should use same amount of space
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(6, 1) # Spacer should claim all unused vertical space (all other rows have 0 stretch)
        grid_layout.setVerticalSpacing(10) # Add padding between rows


    @QtCore.Slot(int)
    def focus_letter(self, index: int):
        if index in range(0, len(self.letters)):
            self.letters[index].setFocus()
            # Move cursor to the end of the letter if needed
            if len(self.letters[index].text()) > 0:
                self.letters[index].setCursorPosition(1)


    @QtCore.Slot()
    def find_words(self):
        global remaining_letters
        global required_letters
        global word_count

        # reset remaining letters if needed
        if len(remaining_letters) != 26:
            remaining_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

        # reset required letters if needed
        if len(required_letters) > 0:
            required_letters = []

        # reset word count
        word_count = 0

        # clear text box
        self.found_words.setText('')

        # get word from the 5 input letters
        word: str = ''
        for letter in self.letters:
            if letter.text() == '':
                word += '_'
            else:
                word += letter.text()

        # remove letters that are know to not be in word
        for letter in self.exclude_letters.text():
            if letter in remaining_letters:
                remaining_letters.remove(letter)

        # get letters that must be in word
        for letter in self.include_letters.text():
            required_letters.append(letter)

        # get number of missing letters
        num_missing: int = word.count('_')

        # generate possible words
        if num_missing == 1:
            self.missing_1(word)
        elif num_missing == 2:
            self.missing_2(word)
        elif num_missing == 3:
            self.missing_3(word)
        elif num_missing == 4:
            self.missing_4(word)
        elif num_missing == 5:
            self.missing_5()

        # if no words were found
        if word_count == 0:
            self.found_words.setText('No words found')


    def missing_1(self, word: str):
        # for each remaining letter
        for let in remaining_letters:
            new_word = ''
            for old_let in word:
                if old_let == '_':
                    new_word += let
                else:
                    new_word += old_let
            self.check_and_add(new_word)


    def missing_2(self, word: str):
        # for all possible letter combinations
        for let_1 in remaining_letters:
            for let_2 in remaining_letters:
                new_word = ''
                count = 0
                # create new word with letters substituted in
                for let in word:
                    if let == '_' and count == 0:
                        new_word += let_1
                        count += 1
                    elif let == '_':
                        new_word += let_2
                    else:
                        new_word += let
                self.check_and_add(new_word)


    def missing_3(self, word: str):
        # for all possible letter combinations
        for let_1 in remaining_letters:
            for let_2 in remaining_letters:
                for let_3 in remaining_letters:
                    new_word = ''
                    count = 0
                    # create new word with letters substituted in
                    for let in word:
                        if let == '_' and count == 0:
                            new_word += let_1
                            count += 1
                        elif let == '_' and count == 1:
                            new_word += let_2
                            count += 1
                        elif let == '_':
                            new_word += let_3
                        else:
                            new_word += let
                    self.check_and_add(new_word)


    def missing_4(self, word: str):
        # for all possible letter combinations
        for let_1 in remaining_letters:
            for let_2 in remaining_letters:
                for let_3 in remaining_letters:
                    for let_4 in remaining_letters:
                        new_word = ''
                        count = 0
                        # create new word with letters substituted in
                        for let in word:
                            if let == '_' and count == 0:
                                new_word += let_1
                                count += 1
                            elif let == '_' and count == 1:
                                new_word += let_2
                                count += 1
                            elif let == '_' and count == 2:
                                new_word += let_3
                                count += 1
                            elif let == '_':
                                new_word += let_4
                            else:
                                new_word += let
                        self.check_and_add(new_word)


    def missing_5(self):
        global word_count
        if len(remaining_letters) == 26 and len(required_letters) == 0:
            self.found_words.setText('Please enter\nsome info')
            word_count = -1 # If word count is 0, this text will be overwritten at the end of find_words function
        else:
            # for all possible letter combinations
            for let_1 in remaining_letters:
                for let_2 in remaining_letters:
                    for let_3 in remaining_letters:
                        for let_4 in remaining_letters:
                            for let_5 in remaining_letters:
                                new_word = let_1 + let_2 + let_3 + let_4 + let_5
                                self.check_and_add(new_word)


    def check_and_add(self, word:str):
        global word_count
        valid = True
        # check if word exists
        if not my_dict.check(word):
            valid = False
        # check if word contains required letters
        for letter in required_letters:
            if letter not in word:
                valid = False
        # add word to textbox if it is valid
        if valid:
            self.found_words.append(word)
            word_count += 1


class LetterBox(QtWidgets.QLineEdit):
    # Create singal for changing focus to a different letter
    change_focus: QtCore.Signal = QtCore.Signal(int)


    def __init__(self, index: int):
        super().__init__()
        self.index: int = index
        self.setFixedWidth(25) # Make these small
        # Add connection for when text is edited by user
        _ = self.textEdited.connect(self.modify_text)


    @QtCore.Slot(str)
    def modify_text(self, text: str):
        changed: bool = False

        # if user entered more than 1 letter, remove extra letters
        if len(text) > 0:
            char: str = text[-1].upper()
            if char.isalpha():
                self.setText(char)
                changed = True
            # clear the text box if space is pressed
            elif char == ' ':
                self.setText('')
                changed = True
            elif text[0].isalpha():
                self.setText(text[0])
            else:
                self.setText('')
        # Center text
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Move to next letter after typing a letter or after pressing space
        if changed:
            self.change_focus.emit(self.index + 1)


    @override
    def keyPressEvent(self, arg__1: QtGui.QKeyEvent, /) -> None:
        # If the left arrow was pressed, go to previous letter
        if arg__1.key() == QtCore.Qt.Key.Key_Left:
            self.change_focus.emit(self.index - 1)
        # If the right arrow was pressed, go to next letter
        elif arg__1.key() == QtCore.Qt.Key.Key_Right:
            self.change_focus.emit(self.index + 1)
        # If backspace was pressed, clear text then go to previous letter
        elif arg__1.key() == QtCore.Qt.Key.Key_Backspace:
            self.setText('')
            self.change_focus.emit(self.index - 1)
        # Use normal key handler if any other key is pressed
        else:
            super().keyPressEvent(arg__1)


class InputBox(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(10) # Let these get shrunk down
        # Add connection for when text is edited by user
        _ = self.textEdited.connect(self.modify_text)


    @QtCore.Slot(str)
    def modify_text(self, text: str):
        text = text.upper()

        # if user entered non-alpha character, or a repeat letter remove it
        if len(text) > 0:
            lastLetter = text[-1]
            if not lastLetter.isalpha() or lastLetter in text[:-1]:
                self.setText(text[:-1])
            else:
                self.setText(text)


if __name__ == '__main__':
    # add missing words to dictionary
    for word in added_words:
        my_dict.add(word)
    
    app = QtWidgets.QApplication([])

    # Match OS light/dark theme
    qdarktheme.setup_theme('auto')

    # get max allowed dimensions for window (May use in the future, for now unused)
    screen: QtGui.QScreen = QtGui.QGuiApplication.primaryScreen()
    max_width: int = screen.availableSize().width()
    max_heigth: int = screen.availableSize().height()

    widget = WordleHelper()
    widget.resize(10, 10) # Make window smallest possible size
    widget.show()

    sys.exit(app.exec())
