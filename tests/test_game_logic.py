import os
import random

from streamlit.testing.v1 import AppTest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

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


# --- check_guess (additional cases) ---


def test_check_guess_accepts_string_secret():
    # check_guess casts both sides to int, so a string secret should behave
    # the same as an int secret.
    outcome, _ = check_guess(50, "50")
    assert outcome == "Win"


def test_check_guess_accepts_string_guess():
    outcome, _ = check_guess("60", 50)
    assert outcome == "Too High"


def test_check_guess_with_negative_numbers():
    outcome, _ = check_guess(-5, -10)
    assert outcome == "Too High"

    outcome, _ = check_guess(-10, -5)
    assert outcome == "Too Low"


def test_check_guess_messages():
    _, win_message = check_guess(50, 50)
    assert win_message == "🎉 Correct!"

    _, high_message = check_guess(60, 50)
    assert high_message == "📈 Go HIGHER!"

    _, low_message = check_guess(40, 50)
    assert low_message == "📉 Go LOWER!"


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


# --- App-level regression tests ---


def test_attempts_start_at_zero_on_fresh_game():
    at = _fresh_app()
    assert at.session_state["attempts"] == 0
    assert "Attempts left: 8" in at.info[0].value  # Normal difficulty, limit 8


def test_hint_shows_correct_range_for_each_difficulty():
    # Regression: the hint used to always say "between 1 and 100" no
    # matter which difficulty (and thus range) was selected.
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)

    at.selectbox[0].set_value("Easy")
    at.run(timeout=30)
    assert "between 1 and 20" in at.info[0].value

    at.selectbox[0].set_value("Hard")
    at.run(timeout=30)
    assert "between 1 and 50" in at.info[0].value

    at.selectbox[0].set_value("Normal")
    at.run(timeout=30)
    assert "between 1 and 100" in at.info[0].value


def test_first_guess_win_scores_ninety():
    # Regression: attempts was incremented before update_score was called,
    # so attempt_number was off by one and a first-guess win scored 80
    # instead of the intended 90.
    at = _fresh_app()
    at.session_state["secret"] = 42
    at.text_input[0].set_value("42")
    at.button[0].click().run(timeout=30)
    assert at.session_state["score"] == 90


def test_losing_after_using_all_attempts():
    at = _fresh_app()
    at.session_state["secret"] = 42
    for _ in range(8):  # Normal difficulty allows 8 attempts
        at.text_input[0].set_value("1")
        at.button[0].click().run(timeout=30)
    assert at.session_state["status"] == "lost"
    assert at.session_state["attempts"] == 8


def test_new_game_clears_the_guess_input_box():
    # Regression: New Game reset the game state but left the old guess
    # text sitting in the input box because the widget's key never changed.
    at = _fresh_app()
    at.text_input[0].set_value("42")
    at.button[0].click().run(timeout=30)  # Submit Guess
    assert at.text_input[0].value == "42"

    at.button[1].click().run(timeout=30)  # New Game
    assert at.text_input[0].value == ""


def test_decimal_guess_is_rejected_end_to_end():
    at = _fresh_app()
    at.text_input[0].set_value("5.5")
    at.button[0].click().run(timeout=30)
    assert at.error[0].value == "Enter a whole number, not a decimal."
    assert at.session_state["history"] == ["5.5"]


# FIX regression: invalid guesses used to consume an attempt even though
# they were never checked against the secret.
def test_invalid_guess_does_not_consume_an_attempt():
    at = _fresh_app()
    at.text_input[0].set_value("banana")
    at.button[0].click().run(timeout=30)
    assert at.session_state["attempts"] == 0

    at.text_input[0].set_value("5.5")
    at.button[0].click().run(timeout=30)
    assert at.session_state["attempts"] == 0


def test_valid_guess_still_consumes_an_attempt():
    at = _fresh_app()
    at.text_input[0].set_value("1")
    at.button[0].click().run(timeout=30)
    assert at.session_state["attempts"] == 1


# --- get_range_for_difficulty ---


def test_range_for_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_for_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_range_for_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)


def test_range_for_unknown_difficulty_defaults_to_normal():
    assert get_range_for_difficulty("Nonsense") == (1, 100)


# --- parse_guess ---


def test_parse_guess_valid_integer_string():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


# FIX: Used Claude to update this test after parse_guess started rejecting
# decimal input instead of silently truncating it.
def test_parse_guess_float_string_is_rejected():
    ok, value, err = parse_guess("42.9")
    assert ok is False
    assert value is None
    assert err == "Enter a whole number, not a decimal."


def test_parse_guess_none_is_rejected():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_guess_empty_string_is_rejected():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_guess_non_numeric_is_rejected():
    ok, value, err = parse_guess("banana")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_negative_integer_string():
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None


def test_parse_guess_plus_prefixed_integer_string():
    ok, value, err = parse_guess("+7")
    assert ok is True
    assert value == 7
    assert err is None


def test_parse_guess_whitespace_padded_integer_string():
    ok, value, err = parse_guess(" 42 ")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_whitespace_only_is_rejected():
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_negative_decimal_is_rejected():
    ok, value, err = parse_guess("-5.5")
    assert ok is False
    assert value is None
    assert err == "Enter a whole number, not a decimal."


def test_parse_guess_scientific_notation_is_rejected():
    # "1e3" has no ".", so it skips the decimal check, but int() still
    # can't parse it directly.
    ok, value, err = parse_guess("1e3")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_leading_zeros_are_accepted():
    ok, value, err = parse_guess("007")
    assert ok is True
    assert value == 7
    assert err is None


def test_parse_guess_out_of_range_number_still_parses():
    # parse_guess has no notion of difficulty bounds; a wildly
    # out-of-range guess should still parse fine (see check_guess,
    # which just reports it as "Too High").
    ok, value, err = parse_guess("99999")
    assert ok is True
    assert value == 99999
    assert err is None


# --- update_score ---


def test_update_score_win_awards_points():
    score = update_score(current_score=0, outcome="Win", attempt_number=0)
    assert score == 90  # 100 - 10 * (0 + 1)


def test_update_score_win_never_awards_less_than_ten():
    score = update_score(current_score=0, outcome="Win", attempt_number=9)
    assert score == 10


def test_update_score_win_awards_fewer_points_on_later_attempts():
    score = update_score(current_score=0, outcome="Win", attempt_number=3)
    assert score == 60  # 100 - 10 * (3 + 1)


def test_update_score_win_floor_boundary():
    # attempt_number=8 lands exactly on the floor without needing to clamp
    score = update_score(current_score=0, outcome="Win", attempt_number=8)
    assert score == 10


def test_update_score_win_floor_holds_far_past_boundary():
    score = update_score(current_score=0, outcome="Win", attempt_number=50)
    assert score == 10


def test_update_score_too_high_deducts_points():
    score = update_score(current_score=50, outcome="Too High", attempt_number=1)
    assert score == 45


# FIX regression: "Too High" used to alternate +5/-5 depending on whether
# attempt_number was even or odd. It should always deduct, same as "Too Low".
def test_update_score_too_high_deducts_points_on_even_attempt():
    score = update_score(current_score=50, outcome="Too High", attempt_number=2)
    assert score == 45


def test_update_score_too_high_deducts_points_on_odd_attempt():
    score = update_score(current_score=50, outcome="Too High", attempt_number=3)
    assert score == 45


def test_update_score_too_low_deducts_points():
    score = update_score(current_score=50, outcome="Too Low", attempt_number=1)
    assert score == 45


def test_update_score_wrong_guess_can_take_score_negative():
    # There is no floor for wrong guesses, only for wins.
    score = update_score(current_score=0, outcome="Too High", attempt_number=1)
    assert score == -5


def test_update_score_unknown_outcome_is_unchanged():
    score = update_score(current_score=50, outcome="Invalid", attempt_number=1)
    assert score == 50
