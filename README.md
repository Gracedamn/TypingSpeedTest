# ⌨️ Typing Speed & Accuracy Test

A terminal-based Python typing game where players improve their typing speed and accuracy through three competitive game modes, a persistent leaderboard, and real-time mistake detection.

---

## Requirements

- Python 3.7+
- No external libraries required — uses only Python standard library (`time`, `random`, `datetime`, `difflib`, `os`, `sys`, `termios`/`msvcrt`)

---

## How to Run

```
python3 typing_speed_test.py
```

The program automatically saves and loads leaderboard data from `leaderboard.txt`, stored in the same folder as the script.

---

## Game Modes

### 🎯 Standard Typing Test
Type a sentence selected from the sentence bank as fast and accurately as possible. Your WPM and accuracy are recorded and saved to the leaderboard.

### ⏱️ Timed Challenge
Type as many sentences as possible within **60 seconds**. All 10 sentences in the chosen difficulty appear once before any repeats — no duplicates until the full set has been shown. Your effective WPM across the full duration is saved.

### 💀 Sudden Death *(real-time mode)*
Characters are judged **instantly as you type** — no Enter required. One wrong keystroke or backspace ends the game immediately. Your score is the number of sentences you survived (your streak).

---

## Main Features

- **Three difficulty levels** — Easy, Medium, and Hard with Python-themed sentences
- **LCS-based accuracy** — uses Longest Common Subsequence matching so extra or missing words anywhere in the sentence do not cause unfair cascading errors
- **Real-time keypress detection** — Sudden Death reads each character the moment it is pressed using terminal raw mode (`termios` / `msvcrt`)
- **ASCII progress bar** — visual accuracy display after every test
- **Rank & badge system** — earn titles from 🐢 Beginner to 👑 Transcendent based on WPM
- **Mistake highlighter** — shows exactly which words were wrong, missing, or extra after each test
- **Persistent leaderboard** — scores survive between sessions via File I/O to `leaderboard.txt`
- **Smart leaderboard ranking** — sorted by accuracy first, then WPM as tiebreaker (prevents key-mashing exploits)
- **Progress tracker** — view your personal WPM and accuracy trend across sessions
- **Erase leaderboard** — clear all records with a confirmation prompt

---

## Menu Options

| Option | Action |
|--------|--------|
| `1` | 🎯 Standard Typing Test |
| `2` | ⏱️ Timed Challenge (60 seconds) |
| `3` | 💀 Sudden Death (real-time keypress) |
| `4` | 🏆 View Leaderboards |
| `5` | 📈 View My Progress |
| `6` | 👤 Change User |
| `7` | 🗑️ Erase All Leaderboard Records |
| `8` | 🚪 Quit |

---

## Sentence Bank

All sentences are **Python course-themed** — covering core concepts, syntax, functions, OOP, and common error types. There are 10 sentences per difficulty level.

| Difficulty | Topics Covered |
|------------|---------------|
| 🟢 Easy | Variables, loops, strings, booleans, lists |
| 🟡 Medium | Functions, classes, dictionaries, try/except, tuples |
| 🔴 Hard | NameError, recursion, LCS, IndexError, lambda, TypeError, generators, KeyError |

---

## Project Files

| File | Description |
|------|-------------|
| `typing_speed_test.py` | Main program — all game logic, classes, and modes |
| `leaderboard.txt` | Auto-generated on first run; stores all player records |

