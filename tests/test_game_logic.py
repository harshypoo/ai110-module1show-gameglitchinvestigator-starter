import os
import random

from streamlit.testing.v1 import AppTest

from logic_utils import check_guess

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression tests for the "New Game" reset bug (app.py, new_game block) ---
# Previously, clicking "New Game" only rerolled the secret. It left `status`
# as "won"/"lost" and never cleared `history`, so the very next rerun hit the
# `status != "playing"` guard and called st.stop() before a new round could
# start, and old guesses stuck around in history.


def _fresh_app():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    return at


def test_new_game_resets_status_after_win():
    at = _fresh_app()
    at.session_state["secret"] = 42
    at.text_input[0].set_value("42")
    at.button[0].click().run(timeout=30)  # Submit Guess -> win
    assert at.session_state["status"] == "won"

    at.button[1].click().run(timeout=30)  # New Game
    assert at.session_state["status"] == "playing"


def test_new_game_resets_status_after_loss():
    at = _fresh_app()
    at.session_state["status"] = "lost"
    at.run(timeout=30)

    at.button[1].click().run(timeout=30)  # New Game
    assert at.session_state["status"] == "playing"


def test_can_play_again_after_new_game():
    # This is the exact symptom reported: after a win/loss, New Game should
    # let you actually submit guesses again instead of being stuck behind
    # the stale "won"/"lost" gate.
    at = _fresh_app()
    at.session_state["secret"] = 42
    at.text_input[0].set_value("42")
    at.button[0].click().run(timeout=30)  # win
    assert at.session_state["status"] == "won"

    at.button[1].click().run(timeout=30)  # New Game

    at.text_input[0].set_value("1")
    at.button[0].click().run(timeout=30)  # Submit Guess again
    assert at.session_state["attempts"] == 1
    assert at.session_state["status"] == "playing"


def test_new_game_clears_history():
    at = _fresh_app()
    at.text_input[0].set_value("5")
    at.button[0].click().run(timeout=30)  # Submit Guess
    assert len(at.session_state["history"]) == 1

    at.button[1].click().run(timeout=30)  # New Game
    assert at.session_state["history"] == []


def test_new_game_resets_score():
    at = _fresh_app()
    at.session_state["secret"] = 42
    at.text_input[0].set_value("42")
    at.button[0].click().run(timeout=30)  # win -> nonzero score
    assert at.session_state["score"] != 0

    at.button[1].click().run(timeout=30)  # New Game
    assert at.session_state["score"] == 0


def test_new_game_resets_attempts():
    at = _fresh_app()
    attempts_before = at.session_state["attempts"]
    at.text_input[0].set_value("5")
    at.button[0].click().run(timeout=30)  # Submit Guess
    assert at.session_state["attempts"] == attempts_before + 1

    at.button[1].click().run(timeout=30)  # New Game
    assert at.session_state["attempts"] == 0


def test_new_game_secret_uses_current_difficulty_range(monkeypatch):
    # Regression: new_game used to always roll random.randint(1, 100),
    # ignoring the selected difficulty's actual (low, high) range.
    calls = []
    original_randint = random.randint

    def recording_randint(a, b):
        calls.append((a, b))
        return original_randint(a, b)

    monkeypatch.setattr(random, "randint", recording_randint)

    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    at.selectbox[0].set_value("Hard")  # Hard -> range (1, 50)
    at.run(timeout=30)

    at.button[1].click().run(timeout=30)  # New Game
    assert calls[-1] == (1, 50)
