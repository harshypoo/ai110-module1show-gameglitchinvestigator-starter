# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
The purpose of this game is to guess a number within a certain amount of tries. You have hints on
going higher or lower as needed.

- [ ] Detail which bugs you found.
I found bugs such as not being able to start a new game, the score not updating correctly, the
hints not updating right, and plenty of more that occurred throughout testing.

- [ ] Explain what fixes you applied.
I fixed the score not updating correctly through changing the calculations, the hints not
updating right by changing how they were applied, deleting the old guess list when starting
a new game, rejecting any non-integer inputs, keeping all guesses within boundaries, and more!

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User enters a guess of 30 when the number is really 55.
2. The game returns "Too Low" and tells the user to "Go Higher". The score is appended to the guess list and the score drops -5.
3. User enters the number 60 and the game returns "Too High" and tells the user to "Go Lower". The guess is appended to the guess list and score drops -5.
4. User enters the number 55. The game shows that it's right and ends as a win. The score is calculated as (your_score) + (100 - 10 * (attempt_number + 1)).
5. Game ends and you can create a new game.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
