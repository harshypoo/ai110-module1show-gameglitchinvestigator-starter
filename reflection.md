# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| | | | | Hint gives a real hint | keeps saying go lower | logic_util.py
| | | | | new game resets old guesses | new game just sets new secret, doesnt get rid of old guesses | logic_utils.py
| | | | | attempts initializes at 1 | attempts initializes at 0 | app.py

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Claude Code

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
Claude suggested that we fix how the "Guess between x and y" is hardcoded and that we should change it
to be the low and high that is input for the current game.

- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
The AI suggested that we leave float inputs from the user alone because it rounds down, but I thought
that was silly and wanted to change it so that float inputs are not allowed at all. I verified my
fix by asking the AI to fix it with erroring the user and then creating test cases. I wanted to make it
so that users know the only possible answers are integers.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
I asked the AI to make different test cases that test the full scope of the issue.

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
I ran a test with pytest to make sure that the game actually reset when pressing New Game.
It showed me that the code was actually resetting the entire board and not just the number.

- Did AI help you design or understand any tests? How?
The AI helped me understand the tests because it named the test and then had comments to
explain what we are doing at that point.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
Streamlit runs your python code from the very beginning every time you rerun the app. It is basically
a wipe of the app and a brand new start. Session state allows us to remember what happened in the
previous games so that we are not losing our memory!

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
I want to make it more of a habit to search for the bug and understand what it does before immediately
asking AI to help me find all the bugs and fix it. I can do one final run and ask AI what bugs
remain, but that should not be the first step.

- This could be a testing habit, a prompting strategy, or a way you used Git.
I also want to make it more of a habit to commit the changes that I make with Git very often.

- What is one thing you would do differently next time you work with AI on a coding task?
I would do more testing on the app in real time rather than just finding bugs and fixing them.
I honestly just fixed them and did not test them ASAP.

- In one or two sentences, describe how this project changed the way you think about AI generated code.
I understand that AI cannot fix everything all the time. Every change requires human input, but
it is a great guide to help you understand what you are doing.