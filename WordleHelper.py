import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import enchant

my_dict = enchant.Dict('en_US')
added_words = ['aunty', 'leapt', 'aider', 'agora', 'leant', 'abled', 'gayly', 'golem', 'haute', 'fibre', 'pinky',
               'briar', 'iliac', 'caddy', 'masse', 'donut', 'plier', 'snuck', 'octad', 'utile', 'ombre', 'flyer',
               'loupe', 'rebar', 'ramen', 'ovine', 'sheik', 'crump', 'doula', 'chuff', 'folky', 'primo', 'eying',
               'caput', 'petri', 'chica', 'droit', 'recut', 'carte', 'vaper', 'ungag', 'loofa', 'cyber', 'convo',
               'kiddy', 'piler', 'rewax', 'panko', 'lacer', 'retag', 'annal', 'glute', 'pinot', 'aioli', 'laddy']
remaining_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                     'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
required_letters = []
word_count = 1


def main():
    # add missing words to dictionary
    for word in added_words:
        my_dict.add(word)

    window = tk.Tk()

    window.title('Wordle Helper')

    window_width = 400
    window_height = 230

    # get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # get coordinates for centering window
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    # position window in the middle of the screen
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    # don't let the window be resizeable
    window.resizable(False, False)

    # set columns for window
    window.columnconfigure(0, weight=4)
    window.columnconfigure(1, weight=1)
    window.columnconfigure(2, weight=4)

    # create word input
    word_frame = ttk.Frame(window)

    l1_text = tk.StringVar()
    l1_box = ttk.Entry(word_frame, width=2, justify='center', textvariable=l1_text)
    l1_box.bind('<Right>', lambda *args: go_next(l2_box))
    l1_text.trace('w', lambda *args: character_limit(l1_text, l2_box))
    l1_box.grid(column=0, row=0)

    l2_text = tk.StringVar()
    l2_box = ttk.Entry(word_frame, width=2, justify='center', textvariable=l2_text)
    l2_box.bind('<BackSpace>', lambda *args: go_back(l1_box))
    l2_box.bind('<Left>', lambda *args: go_back(l1_box))
    l2_box.bind('<Right>', lambda *args: go_next(l3_box))
    l2_text.trace('w', lambda *args: character_limit(l2_text, l3_box))
    l2_box.grid(column=1, row=0)

    l3_text = tk.StringVar()
    l3_box = ttk.Entry(word_frame, width=2, justify='center', textvariable=l3_text)
    l3_box.bind('<BackSpace>', lambda *args: go_back(l2_box))
    l3_box.bind('<Left>', lambda *args: go_back(l2_box))
    l3_box.bind('<Right>', lambda *args: go_next(l4_box))
    l3_text.trace('w', lambda *args: character_limit(l3_text, l4_box))
    l3_box.grid(column=2, row=0)

    l4_text = tk.StringVar()
    l4_box = ttk.Entry(word_frame, width=2, justify='center', textvariable=l4_text)
    l4_box.bind('<BackSpace>', lambda *args: go_back(l3_box))
    l4_box.bind('<Left>', lambda *args: go_back(l3_box))
    l4_box.bind('<Right>', lambda *args: go_next(l5_box))
    l4_text.trace('w', lambda *args: character_limit(l4_text, l5_box))
    l4_box.grid(column=3, row=0)

    l5_text = tk.StringVar()
    l5_box = ttk.Entry(word_frame, width=2, justify='center', textvariable=l5_text)
    l5_box.bind('<BackSpace>', lambda *args: go_back(l4_box))
    l5_box.bind('<Left>', lambda *args: go_back(l4_box))
    l5_text.trace('w', lambda *args: character_limit(l5_text, None))
    l5_box.grid(column=4, row=0)

    word_frame.grid(row=0, column=0, pady=10)

    # create label for letters to remove
    remove_label = ttk.Label(window, text="Not in the word:")
    remove_label.grid(row=1, column=0, sticky=tk.W, padx=10)

    # create textbox for letters to remove
    remove_text = tk.StringVar()
    remove_box = ttk.Entry(window, textvariable=remove_text)
    remove_text.trace('w', lambda *args: make_upper(remove_text))
    remove_box.grid(row=2, column=0, sticky=tk.W, padx=10)

    # create label for required letters
    required_label = ttk.Label(window, text="In the word somewhere:")
    required_label.grid(row=3, column=0, sticky=tk.W, padx=10)

    # create textbox for letters to remove
    required_text = tk.StringVar()
    required_box = ttk.Entry(window, textvariable=required_text)
    required_text.trace('w', lambda *args: make_upper(required_text))
    required_box.grid(row=4, column=0, sticky=tk.W, padx=10)

    # create button for running program
    run_button = ttk.Button(window, text='Find Words', command=lambda: find_words(l1_text.get(), l2_text.get(), l3_text.get(), l4_text.get(), l5_text.get(), remove_text.get(), required_text.get(), results))
    run_button.grid(row=5, column=0, pady=10)

    # create text widget for the results
    results = ScrolledText(window, height=13, width=20)
    results.grid(row=0, column=2, rowspan=6, padx=10)
    results['state'] = 'disabled'

    window.mainloop()


def find_words(l1, l2, l3, l4, l5, remove, required, results):
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
    word_count = 1

    # clear text box
    results['state'] = 'normal'
    results.delete('1.0', 'end')
    results['state'] = 'disabled'

    # get word from the 5 input letters
    word = make_word(l1, l2, l3, l4, l5)

    # remove letters that are know to not be in word
    for letter in remove:
        if letter in remaining_letters:
            remaining_letters.remove(letter)

    # get letters that must be in word
    for letter in required:
        required_letters.append(letter)

    # get number of missing letters
    num_missing = word.count('_')

    # generate possible words
    if num_missing == 1:
        missing_1(word, results)
    elif num_missing == 2:
        missing_2(word, results)
    elif num_missing == 3:
        missing_3(word, results)
    elif num_missing == 4:
        missing_4(word, results)
    elif num_missing == 5:
        missing_5(results)

    # if no words were found
    if word_count == 1:
        results['state'] = 'normal'
        results.insert('1.0', 'No words found')
        results['state'] = 'disabled'


def missing_1(word, results):
    # for each remaining letter
    for let in remaining_letters:
        new_word = ''
        for old_let in word:
            if old_let == '_':
                new_word += let
            else:
                new_word += old_let
        check_and_add(new_word, results)


def missing_2(word, results):
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
            check_and_add(new_word, results)


def missing_3(word, results):
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
                check_and_add(new_word, results)


def missing_4(word, results):
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
                    check_and_add(new_word, results)


def missing_5(results):
    if len(remaining_letters) == 26 and len(required_letters) == 0:
        results['state'] = 'normal'
        results.insert('1.0', 'Please enter\nsome info')
        results['state'] = 'disabled'
    else:
        # for all possible letter combinations
        for let_1 in remaining_letters:
            for let_2 in remaining_letters:
                for let_3 in remaining_letters:
                    for let_4 in remaining_letters:
                        for let_5 in remaining_letters:
                            new_word = let_1 + let_2 + let_3 + let_4 + let_5
                            check_and_add(new_word, results)


def check_and_add(word, results):
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
        results['state'] = 'normal'
        results.insert(f'{word_count}.0', f'{word}\n')
        results['state'] = 'disabled'
        word_count += 1


def make_word(l1, l2, l3, l4, l5):
    if l1 == '':
        l1 = '_'
    if l2 == '':
        l2 = '_'
    if l3 == '':
        l3 = '_'
    if l4 == '':
        l4 = '_'
    if l5 == '':
        l5 = '_'
    return l1 + l2 + l3 + l4 + l5


def character_limit(text, next_box):
    cleared = False

    # if user entered more than 1 letter, remove extra letters
    if len(text.get()) > 0:
        char = text.get()[-1].upper()
        if char.isalpha():
            text.set(char)
        # clear the text box if space is pressed
        elif char == ' ':
            text.set('')
            cleared = True
        elif text.get()[0].isalpha():
            text.set(text.get()[0])
        else:
            text.set('')
    # Move to next letter after typing something or after pressing space
    if next_box and (text.get() != '' or cleared):
        next_box.focus()
        next_box.icursor(1)


def make_upper(text):
    # if user entered non-alpha character, remove it
    if len(text.get()) > 0 and not text.get()[-1].isalpha():
        text.set(text.get()[:-1].upper())
    else:
        text.set(text.get().upper())


def go_back(prev):
    if prev:
        prev.focus()


def go_next(next_box):
    if next_box:
        next_box.focus()
        next_box.icursor(1)


if __name__ == '__main__':
    main()
