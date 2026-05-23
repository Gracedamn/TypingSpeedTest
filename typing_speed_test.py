#COMP9001 final project
import os  # import os module for file path handling to ensure leaderboard.txt is saved in the same directory as the script, and for file I/O operations in the "Leaderboard" class
import sys   # import sys.stdin module for real-time keyboard press reading in sudden death mode
import time  # import time module to measure the time taken for each typing session, used in WPM calculation and timed challenge mode
import random  # import random module to select sentences randomly from the sentence bank for each test session
from datetime import datetime   # import datetime module to timestamp each session result for leaderboard display and user progress tracking
from difflib import SequenceMatcher    # import SequenceMatcher module to calculate longest common subsequence (LCS) for accuracy evaluation

'''
Introduction to 3 game modes:
- Standard typing test: simply test your typing accuracy & WPM with Easy / Medium / Hard difficulty
- Timed Challenge: Within 60 seconds time limit, type as many sentences as possible
- Sudden Death: real-time keyboard press detection, one wrong character leads to game over
'''


# Use os.path module to save leaderboard info inside leaderboard.txt in the same directory as the py program, ensuring it works regardless of moving the py file to other directories
script_dir = os.path.dirname(os.path.abspath(__file__))  # get the directory of the current script
leaderboard_file = os.path.join(script_dir, "leaderboard.txt")  # construct the full path to leaderboard.txt in the same directory as the script


# Create built-in sentence-bank dictionary with 10 target sentences per difficulty level
sentence_bank = {
    "easy": 
    ["Python uses indentation to define code blocks",
    "A variable stores a value in memory",
    "The print function displays output to the screen",
    "Lists store multiple items in a single variable",
    "A string is a sequence of characters in Python",
    "Boolean values in Python are either True or False",
    "Comments in Python begin with a hash symbol",
    "The len function returns the length of a sequence",
    "An integer is a whole number without decimal places",
    "Loops are used to repeat a block of code multiple times"],

    "medium": 
    ["A function is defined using the def keyword in Python",
    "The range function generates a sequence of integer numbers",
    "Dictionaries store data as key and value pairs in Python",
    "A class is a blueprint for creating objects in Python",
    "The try and except block is used to catch and handle errors",
    "List comprehensions provide a concise way to create new lists",
    "The return statement exits a function and sends back a value",
    "Tuples are immutable sequences that cannot be modified after creation",
    "The append method adds a new element to the end of a list",
    "Inheritance allows a subclass to reuse methods from a parent class"],

    "hard": 
    ["A NameError occurs when you reference a variable that has not been defined yet",
    "Recursion is a technique where a function calls itself to solve smaller subproblems",
    "The SequenceMatcher class computes the longest common subsequence between two sequences",
    "An IndexError is raised when you attempt to access a list index that is out of range",
    "Lambda functions are anonymous single expression functions defined with the lambda keyword",
    "A TypeError occurs when an operation is applied to an object of an incompatible type",
    "Multidimensional lists are nested lists commonly used to represent grids and matrices",
    "The with statement wraps a block of code using the methods of a context manager object",
    "Generators use the yield keyword to produce a sequence of values one at a time lazily",
    "A KeyError is raised when a dictionary lookup fails to find the specified key in the set"]}

# Suggested WPM targets for each difficulty level, used for contextual feedback in session summary
WPM_scale = {"easy": 90, "medium": 70, "hard": 50}     # these values are based on typical typing speeds for each difficulty level, and are used to provide contextual feedback in the session summary (e.g. "Push your WPM toward 70 next time!" for medium difficulty)


# WPM rank evaluation message, displayed at the session result
rank_tiers = [(100, "👑  Transcendent"), (80,  "⚡  Lightning Fingers"), (60,  "🔥  Speed Demon"), (40,  "✅  Competent Typist"), (20,  "📈  Improving"), (0,   "🐢  Beginner")]
def get_rank(wpm):
    for threshold, title in rank_tiers:
        if wpm >= threshold:
            return title
    return "🐢  Beginner"   # return this string if player wpm=0



# Define a render bar that visually displays accuracy result as a progress bar 
def render_bar(value):
    max_value = 100   # accuracy shall always below 100%
    width = 26   # bar character width with 26 blocks
    fill = "█"   # filled portion character (full block)
    empty = "░"   # empty portion character (light shade)
    ratio = min(value / max_value, 1)   # return the proportion of the bar to fill
    filled = int(ratio * width)
    bar = fill * filled + empty * (width - filled)
    return f"[{bar}]"


'''
Real-time keyboard press reader for Sudden Death mode
Below 2 functions implemented to read one input character at a time from stdin module without waiting for player press "enter" button
❗️AI-generated function code for this advanced feature session❗️
'''
def _read_single_char():
    """
    Read exactly one character from stdin WITHOUT waiting for Enter.

    On macOS / Linux : uses the termios + tty standard library modules
                       to put the terminal in raw mode temporarily.
    On Windows       : falls back to msvcrt.getwch().

    Raw mode means:
      - Characters are sent to the program immediately on each keypress
      - No line buffering, no Enter required
      - Terminal is restored to normal after each character is read
    """
    try:
        import termios, tty
        fd           = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            # ALWAYS restore terminal — even if an exception occurs
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except (ImportError, AttributeError):
        # Windows fallback
        import msvcrt
        return msvcrt.getwch()


def _type_sentence_realtime(sentence):
    """
    Real-time character-by-character input for Sudden Death mode.

    HOW IT WORKS:
      1. Display the target sentence above a blank typing line.
      2. Read each keypress immediately (no Enter required).
      3. If the typed char matches the expected char → echo it, advance.
      4. If wrong char → echo it, return (False, ...) INSTANTLY.
      5. Backspace is treated as an error (you can't fix mistakes here).
      6. Full sentence typed correctly → return (True, ...).

    Returns:
        success      (bool)  : True if sentence completed with no mistakes
        typed        (str)   : characters typed so far
        wrong_char   (str)   : the incorrect character typed (None on success)
        expected_char(str)   : what was expected at that position (None on success)
    """
    print(f"\n  ➡️  {sentence}")
    print("  ", end="", flush=True)

    typed = ""

    for expected in sentence:
        ch = _read_single_char()

        # Ctrl+C — allow graceful quit
        if ch == '\x03':
            print()
            raise KeyboardInterrupt

        # Backspace (0x7f Unix, 0x08 Windows) — treated as a mistake
        if ch in ('\x7f', '\x08'):
            print("⌫", end="", flush=True)
            return False, typed, "⌫", expected

        # Echo the character the user pressed (correct or not)
        print(ch, end="", flush=True)

        if ch == expected:
            typed += ch
        else:
            # Wrong character — return immediately, game over
            return False, typed, ch, expected

    # Reached here = every character matched
    print()   # move to new line after completed sentence
    return True, sentence, None, None




'''
Define TypingSession class to store and evaluate one completed typing test attempt, 
with attributes for username, sentence, user input, spent time, difficulty, date, WPM, and accuracy. 
Include methods to calculate WPM and accuracy, highlight mistakes inline, 
print a summary of the session results, 
and convert the session data into a row format for leaderboard storage.
'''

class TypingSession:

    def __init__(self, username, sentence, user_input, spent_time, difficulty):
        self.username     = username   # player's name
        self.sentence     = sentence   # the target sentence they were supposed to type
        self.user_input   = user_input  # what player actually typed
        self.spent_time = spent_time    # time taken in seconds
        self.difficulty   = difficulty   # easy / medium / hard
        self.date         = datetime.now().strftime("%d-%m-%Y %H:%M")     # timestamp of when the session was completed
        self.wpm          = self.calculate_wpm()     # calculate words per minute based on user input and time spent
        self.accuracy     = self.calculate_accuracy()      # calculate accuracy as a percentage using LCS-based word-level comparison between sentence and user input


    # Calculate WPM using: WPM = (characters typed / 5) / (minutes spent)
    # Standard WPM formula where 5 characters = 1 word, and time is converted to minutes
    def calculate_wpm(self):   
        if self.spent_time == 0:  # avoid division by 0 if time is 0
            return 0.0
        return round((len(self.user_input) / 5) / (self.spent_time / 60), 1)


    # Calculate accuracy using LCS-based word-level comparison. SequenceMatcher finds the longest common subsequence of words, regardless of insertions or deletions anywhere in the input.
    def calculate_accuracy(self):
        sentence_words = self.sentence.split()    # split the target sentence into words
        user_words = self.user_input.split()      # split the user's input into words
        matcher = SequenceMatcher(None, sentence_words, user_words)      # compare the two lists of words
        matched = sum(block.size for block in matcher.get_matching_blocks())       # sum the sizes of all matching blocks to get the total number of correctly matched words
        return round((matched / len(sentence_words)) * 100, 1)         # accuracy = correctly matched words / total words, in percentage without % sign


    '''
    At session result, print the sentence with mistakes marked inline.
    Correct → shown normally
    Wrong   → [✗ WRONG:'typed'→'expected']
    Missing → [✗ MISSING:'word']
    Extra   → [✗ EXTRA:'word']
    '''
    def mistake_breakdown(self):
        sentence_words = self.sentence.split()
        user_words = self.user_input.split()
        parts = []
        for i in range(max(len(sentence_words), len(user_words))):
            if i >= len(user_words): 
                parts.append(f"[✗ MISSING:'{sentence_words[i]}']")
            elif i >= len(sentence_words): 
                parts.append(f"[✗ EXTRA:'{user_words[i]}']")
            elif sentence_words[i] == user_words[i]:    # correct word
                parts.append(sentence_words[i])   
            else: 
                parts.append(f"[✗ WRONG:'{user_words[i]}'→'{sentence_words[i]}']")  
        print("\n  📝 Mistake Breakdown:")
        print("  " + "─" * 54)
        print("  " + " ".join(parts))
        print("  " + "─" * 54)


    '''
    Print result card with following:
    - Accuracy progress bar
    - Rank message based on WPM
    - Contextual feedback
    - Mistake breakdown (function call)
    '''
    def print_summary(self):
        scale = WPM_scale.get(self.difficulty, 70)    # get the WPM target for the difficulty level, default to 70 if difficulty not found

        print("\n" + "=" * 56)
        print("               📊  SESSION RESULTS")
        print("=" * 56)
        print(f"{'Player':<13}: {self.username}")   # left-aligned with 13-char width for neat formatting
        print(f"{'Difficulty':<13}: {self.difficulty.capitalize()}")
        print(f"{'Date':<13}: {self.date}")
        print(f"{'Time Taken':<13}: {round(self.spent_time, 2)}s")
        print(f"{'WPM':<13}: {self.wpm}  (target: {scale})")    # display WPM with target for context
        print()
        # Accuracy bar only — WPM has no natural 0–100% scale so no bar
        print(f"  Accuracy  {render_bar(self.accuracy)}  {self.accuracy}%")
        print()
        print(f"  Rank : {get_rank(self.wpm)}")
        print("=" * 56)

        if self.accuracy < 50:
            print("  💡 Slow down — accuracy matters more than speed!")
        elif self.accuracy < 80:
            print("  📈 Good effort! Aim for 80%+ accuracy next time.")
        elif self.wpm >= scale:
            print(f"  🔥 Outstanding — you beat the {self.difficulty} WPM target!")
        else:
            print(f"  ✅ Accurate! Push your WPM toward {scale} next time.")

        self.mistake_breakdown()


    # Convert session data into a row format for leaderboard storage: [date, username, wpm, accuracy, time, difficulty, mode]
    def to_row(self):
        return [
            self.date,
            self.username,
            self.wpm,
            self.accuracy,
            round(self.spent_time, 2),
            self.difficulty,
            "standard"]






'''
Define a Leaderboard class to manage all records using a 2D list in memory and a .txt file on disk.
'''
class Leaderboard:

    # these indices correspond to the order of fields in the record rows
    column_date = 0             # index of the date field in the record row
    column_username = 1 
    column_WPM = 2
    column_accuracy = 3
    column_time = 4
    column_difficulty = 5
    column_mode = 6  

    # initialize the leaderboard with the given file path, load existing records from the disk
    def __init__(self, filepath=leaderboard_file):  
        self.filepath = filepath
        self.records  = []
        self.load_from_file()
        

    # Parse the saved .txt file into self.records (2D list). Each comma-separated line becomes one row.
    def load_from_file(self):
        self.records = []
        try:
            with open(self.filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) == 7:    # ensure the line has all expected fields before parsing
                        self.records.append([
                            parts[0],    # date
                            parts[1],      # username
                            float(parts[2]),    # WPM
                            float(parts[3]),    # accuracy
                            float(parts[4]),    # time
                            parts[5],     # difficulty
                            parts[6],     # mode
                        ])
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Could not load leaderboard: {e}")

        

    # write self.records to disk
    def save_to_file(self):
        try:
            with open(self.filepath, "w") as f:
                for row in self.records:
                    f.write(",".join(str(v) for v in row) + "\n")
        except Exception as e:
            print(f"Could not save leaderboard: {e}")


    # On leaderboard load, sort self.records by accuracy DESC, then WPM DESC using a tuple sort key
    def sort_records(self):
        self.records.sort(
            key = lambda row: (row[self.column_accuracy], row[self.column_WPM]),     # create a tuple of (accuracy, WPM) for each row to sort by both fields
            reverse = True)   # sort in descending order
        

    # Add a standard TypingSession to the records, then sort and save to disk
    def add_session(self, session):
        self.records.append(session.to_row())
        self.sort_records()
        self.save_to_file()

    # Add a manually constructed record (used by timed & sudden death modes) to the records, then sort and save to disk
    def add_raw_record(self, date, username, wpm, accuracy, spent, difficulty, mode):
        self.records.append([date, username, float(wpm), float(accuracy), round(float(spent), 2), difficulty, mode])
        self.sort_records()
        self.save_to_file()



    # Clear all leaderboard records from the disk
    def erase_all(self):
        self.records = []
        self.save_to_file()



    # Display top n records for a given mode
    def display_top(self, mode = "standard", n = 10):    # default to show top 10 records for the specified mode

        mode_labels = {
            "standard": "🏆  STANDARD LEADERBOARD",
            "timed": "⏱️   TIMED CHALLENGE LEADERBOARD",
            "sudden_death": "💀  SUDDEN DEATH LEADERBOARD",}
        filtered = [r for r in self.records if r[self.column_mode] == mode]  # filter records to only include those matching the specified mode (standard, timed, or sudden death)

        print("\n" + "=" * 72)
        print(f"  {mode_labels.get(mode, 'LEADERBOARD')}")
        if mode == "standard":
            print("  Ranked by: Accuracy first, WPM as tiebreaker")
        print("=" * 72)

        if mode == "sudden_death":
            print(f"  {'No.':<5}    {'Name':<16} {'Streak':>8}  {'Difficulty':<12} {'Date'}")

        else:     # for standard and timed modes, show accuracy and WPM columns
            print(f"  {'No.':<5}    {'Name':<16} {'Accuracy':>9}  {'WPM':>7}  {'Difficulty':<12} {'Date'}")
        print("─" * 72)

        if not filtered:
            print(f"  No {mode.replace('_', ' ')} records yet.")
        else:  
            # medal = emoji (2 display cols) or "  " (also 2 display cols)
            # This keeps name-column start at the same position for every row.
            medals = ["🥇", "🥈", "🥉"]
            for i, row in enumerate(filtered[:n]):
                rank_num = f"{i + 1}." 
                medal    = medals[i] if i < 3 else "  "   # both = 2 display cols
                diff     = row[self.column_difficulty].capitalize()

                if mode == "sudden_death":
                    print(f"  {rank_num:<5}  {medal}  "
                          f"{row[self.column_username]:<16} "
                          f"{int(row[self.column_WPM]):>8}  "
                          f"{diff:<12} {row[self.column_date]}")
                else:
                    print(f"  {rank_num:<5}  {medal}  "
                          f"{row[self.column_username]:<16} "
                          f"{str(row[self.column_accuracy]) + '%':>9}  "
                          f"{row[self.column_WPM]:>7}  "
                          f"{diff:<12} {row[self.column_date]}")
        print("=" * 72)


    # Display all three modes in sequence in leaderboard
    def display_all_leaderboards(self):
        self.display_top(mode="standard")
        self.display_top(mode="timed")
        self.display_top(mode="sudden_death")


    # Show standard-mode records for one user sorted by time, then summarise WPM and accuracy improvement.
    def display_user_progress(self, username):
        rows = [r for r in self.records     # filter to only include records where the username matches and mode is standard
                if r[self.column_username] == username
                and r[self.column_mode]    == "standard"]

        if not rows:
            print(f"\n  No standard mode history found for '{username}'.")
            return

        rows.sort(key=lambda r: r[self.column_date])   # sort the user's records by date

        print(f"\n{'=' * 62}")
        print(f"  📈  Progress Report — {username}")
        print(f"{'=' * 62}")
        print(f"  {'#':<5} {'WPM':<8} {'Accuracy':<12} {'Difficulty':<12} {'Date'}")
        print("─" * 62)

        for i, row in enumerate(rows):
            print(f"  {i+1:<5} {row[self.column_WPM]:<8} "
                  f"{str(row[self.column_accuracy])+'%':<12} "
                  f"{row[self.column_difficulty].capitalize():<12} "
                  f"{row[self.column_date]}")
            

        # If user has 2 or more records, show improvement from first to latest session
        if len(rows) >= 2:
            first, latest = rows[0], rows[-1]
            dw = round(latest[self.column_WPM]      - first[self.column_WPM],      1)  # calculate WPM improvement from first to latest session
            da = round(latest[self.column_accuracy] - first[self.column_accuracy], 1)
            print(f"\n  WPM      {first[self.column_WPM]} → {latest[self.column_WPM]}"
                  f"   ({'↑' if dw >= 0 else '↓'}{abs(dw)} WPM)")
            print(f"  Accuracy {first[self.column_accuracy]}% → {latest[self.column_accuracy]}%"
                  f"   ({'↑' if da >= 0 else '↓'}{abs(da)}%)")
            print(f"  Current Rank : {get_rank(latest[self.column_WPM])}")
        print("=" * 62)






# Prompts the user to choose a difficulty level
def choose_difficulty():
    print("\n  Select Difficulty:")
    print("  1. 🟢 Easy   — short Python basics")
    print("  2. 🟡 Medium — functions, OOP, errors")
    print("  3. 🔴 Hard   — advanced concepts and error types")

    while True:
        try:
            choice = input("  Choice (1-3): ").strip()
            if choice == "1": return sentence_bank["easy"],   "easy"
            if choice == "2": return sentence_bank["medium"], "medium"
            if choice == "3": return sentence_bank["hard"],   "hard"
            raise ValueError("Please enter 1, 2, or 3.")
        except ValueError as e:
            print(f"{e}")  
            continue




# Define UI after user selects standard typing test mode
def run_standard_test(username, leaderboard):
    sentences, difficulty = choose_difficulty()
    sentence = random.choice(sentences)

    print("\n" + "=" * 60)
    print("  ⌨️   TYPE THE SENTENCE BELOW — exactly as shown!")
    print("=" * 60)
    print(f"\n  ➡️  {sentence}\n")
    input("  Press ENTER when ready...")
    print("\n  GO! ⬇️\n  ", end="", flush=True)

    start = time.time()
    user_input = input()
    spent = time.time() - start

    session = TypingSession(username, sentence, user_input, spent, difficulty)
    session.print_summary()
    leaderboard.add_session(session)
    print("  ✅ Score saved to leaderboard!\n")



# Define UI after user selects timed challenge mode
def run_timed_challenge(username, leaderboard):
    duration  = 60      # time limit 60sec
    sentences, difficulty = choose_difficulty()

    print("\n" + "=" * 60)
    print(f"  ⏱️   TIMED CHALLENGE — {duration} seconds!")
    print("  Type each sentence accurately. A new one appears after each.")
    print("=" * 60)
    input("\n  Press ENTER to start the clock...")

    start = time.time()
    total_correct_words = 0
    total_target_words = 0
    rounds = 0
    per_round_acc = []

    sentence_queue = sentences.copy()     
    random.shuffle(sentence_queue)    # shuffle the sentences to create a random order for the first cycle
    cycle = 1

    while True:
        spent   = time.time() - start
        remaining = duration - spent

        if remaining <= 0:
            break

        # Refill queue when exhausted — new shuffled order each cycle
        if not sentence_queue:
            sentence_queue = sentences.copy()
            random.shuffle(sentence_queue)
            cycle += 1
            print(f"\n  🔁 All sentences shown — starting cycle {cycle}!")

        sentence = sentence_queue.pop(0)    # always take from the front

        print(f"\n  ⏳ {int(remaining)}s left  |  Round {rounds + 1}")
        print(f"  ➡️  {sentence}")
        print("  ", end="", flush=True)

        user_input = input()

        sentence_words = sentence.split()
        user_words = user_input.split()
        matched = sum(b.size for b in SequenceMatcher(None, sentence_words, user_words).get_matching_blocks())
        acc = round((matched / len(sentence_words)) * 100, 1) if sentence_words else 0.0     # calculate accuracy for this round

        total_correct_words += matched
        total_target_words  += len(sentence_words)
        per_round_acc.append(acc)
        rounds += 1

        status = "✅ Perfect!" if acc == 100.0 else f"⚠️  {acc}%"
        print(f"  {status}  |  Correct words so far: {total_correct_words}")

        # time check after processing input to ensure the last round counts if completed within time, but exits immediately if time is up before starting next round
        if time.time() - start >= duration:     
            break

    overall_acc = round((total_correct_words / total_target_words * 100), 1) \
                  if total_target_words > 0 else 0.0   
    eff_wpm     = round((total_correct_words / 5) / (duration / 60), 1)

    print("\n" + "=" * 56)
    print("            ⏱️   TIMED CHALLENGE RESULTS")
    print("=" * 56)
    print(f"  Sentences attempted   : {rounds}")
    print(f"  Total correct words   : {total_correct_words} / {total_target_words}")
    print(f"  Effective WPM         : {eff_wpm}  (target: {WPM_scale[difficulty]})")
    print()
    print(f"  Accuracy  {render_bar(overall_acc)}  {overall_acc}%")
    print()
    print(f"  Rank : {get_rank(eff_wpm)}")
    print("=" * 56)

    now = datetime.now().strftime("%d-%m-%Y %H:%M")   # timestamp for when the timed challenge session was completed
    leaderboard.add_raw_record(now, username, eff_wpm, overall_acc,
                                duration, difficulty, "timed")
    print("  ✅ Timed score saved!\n")




## Define UI after user selects sudden death mode
def run_sudden_death(username, leaderboard):

    sentences, difficulty = choose_difficulty()

    print("\n" + "=" * 60)
    print("  💀  SUDDEN DEATH — REAL-TIME MODE")
    print("─" * 60)
    print("  ⚡ Each keystroke is judged INSTANTLY.")
    print("  ❌ One wrong character = GAME OVER immediately.")
    print("  🚫 Backspace counts as a mistake.")
    print("  ✅ Type the full sentence correctly to advance.")
    print("=" * 60)
    input("\n  Press ENTER when ready")

    streak = 0    # counts how many sentences the player has completed without a mistake
    total_time = 0.0

    while True:              # runs until a mistake triggers break
        sentence = random.choice(sentences)
        print(f"\n  💀 Streak: {streak}")

        t_start = time.time()    # start time for this sentence
        try:
            success, typed, wrong_char, expected_char = _type_sentence_realtime(sentence)
        except KeyboardInterrupt:
            print("\n  ⚠️  Game interrupted.")
            break
        spent = time.time() - t_start
        total_time += spent

        if success:
            streak += 1
            print(f"  ✅ Perfect!  Streak: {streak} 🔥")
        else:
            print(f"\n  💀 GAME OVER!")
            if wrong_char and expected_char:
                print(f"  Expected '{expected_char}'  but you typed '{wrong_char}'")
            print(f"  Final Streak: {streak} sentence(s)")
            break

    print("\n" + "=" * 54)
    print("            💀  SUDDEN DEATH RESULTS")
    print("=" * 54)
    print(f"  Final Streak : {streak} sentence(s) survived")
    print(f"  Rank         : {get_rank(streak * 10)}")
    print("=" * 54)

    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    leaderboard.add_raw_record(now, username, float(streak), 100.0,
                                total_time if total_time > 0 else 0.0,
                                difficulty, "sudden_death")
    print(f"  ✅ Streak of {streak} saved!\n")



# Get and validate username
def get_username():
    while True:
        try:
            name = input("\n  Enter your username: ").strip()
            if not name:
                raise ValueError("Username cannot be empty.")
            if len(name) > 20:
                raise ValueError("Username must be 20 characters or fewer.")
            if "," in name:
                raise ValueError("Username cannot contain commas.")
            return name
        except ValueError as e:
            print(f"{e}")


# Display the main menu with options
def display_menu(username):
    print("\n" + "=" * 48)
    print("        ⌨️   TYPING SPEED & ACCURACY TEST")
    print("=" * 48)
    print(f"  👤  Logged in as : {username}")
    print("─" * 48)
    print("  1.  🎯  Standard Typing Test")
    print("  2.  ⏱️   Timed Challenge  (60 seconds)")
    print("  3.  💀  Sudden Death  (real-time keypress)")
    print("  4.  🏆  View Leaderboards")
    print("  5.  📈  View My Progress")
    print("  6.  👤  Change User")
    print("  7.  🗑️   Erase All Leaderboard Records")
    print("  8.  🚪  Quit")
    print("=" * 48)


# Validate user input for menu choice
def get_menu_choice(max_choice = 8):
    valid = [str(i) for i in range(1, max_choice + 1)]
    while True:
        try:
            choice = input(f"  Your choice (1–{max_choice}): ").strip()
            if choice not in valid:
                raise ValueError(f"Please enter a number from 1 to {max_choice}.")
            return choice
        except ValueError as e:
            print(f"{e}")
            continue


'''
Ask the user to confirm before erasing all records. 
Requires typing 'YES' to proceed.
'''
def confirm_erase(leaderboard):
    print("\n  ⚠️  WARNING: This will permanently delete ALL leaderboard records!")
    print(f"  (File: {leaderboard.filepath})")
    confirm = input("  Type YES to confirm, anything else to cancel: ").strip()
    if confirm == "YES":
        leaderboard.erase_all()
        print("  ✅ All leaderboard records have been erased.")
    else:
        print("  ❌ Cancelled — no records were deleted.")




# Dispatches menu choices to the appropriate game mode or action.
def main():

    leaderboard = Leaderboard()

    print("\n  🎯  Welcome to the Typing Speed & Accuracy Test!")
    print("  Improve your Python knowledge and your typing speed.\n")
    print(f"  💾  Leaderboard stored at: {leaderboard_file}")
    username = get_username()

    while True:
        display_menu(username)
        choice = get_menu_choice()

        if choice == "1": 
            run_standard_test(username, leaderboard)
        elif choice == "2": 
            run_timed_challenge(username, leaderboard)
        elif choice == "3": 
            run_sudden_death(username, leaderboard)
        elif choice == "4": 
            leaderboard.display_all_leaderboards()
        elif choice == "5": 
            leaderboard.display_user_progress(username)
        elif choice == "6":
            username = get_username()
            print(f"  👤 sentence_wordsitched to: {username}")
        elif choice == "7": 
            confirm_erase(leaderboard)
        elif choice == "8":
            print("\n  👋 Thanks for playing! Keep practising!\n")
            break


if __name__ == "__main__":
    main()
