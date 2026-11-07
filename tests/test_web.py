import pytest

from data.config import ALL_WORDS_ENGLISH, ALL_WORDS_ARABIC
from env.wordle_env import get_feedback
from web import game as games
from web.app import app

WORDS = {"en": set(ALL_WORDS_ENGLISH), "ar": set(ALL_WORDS_ARABIC)}
SECRET = {"en": "crane", "ar": ALL_WORDS_ARABIC[0]}


@pytest.fixture
def client():
    return app.test_client()


def new_game(client, language="en", word=None):
    body = {"language": language}
    if word:
        body["word"] = word
    response = client.post("/api/games", json=body)
    assert response.status_code == 201, response.json
    return response.json["id"]


def wrong_words(language, secret, count):
    return [w for w in sorted(WORDS[language]) if w != secret][:count]


def test_index_serves_the_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"/static/app.js" in response.data
    assert client.get("/static/app.js").status_code == 200


@pytest.mark.parametrize("language", ["en", "ar"])
def test_random_word_comes_from_the_word_list(client, language):
    response = client.get(f"/api/random-word?language={language}")
    assert response.status_code == 200
    assert response.json["word"] in WORDS[language]


@pytest.mark.parametrize("body, error", [
    ({"language": "fr"}, "unknown_language"),
    ({}, "unknown_language"),
    ({"language": ["en"]}, "unknown_language"),
    ({"language": "en", "word": "cra"}, "not_enough_letters"),
    ({"language": "en", "word": "zzzzz"}, "not_in_word_list"),
    ({"language": "en", "word": 12345}, "not_enough_letters"),
    ({"language": "ar", "word": "crane"}, "not_in_word_list"),
])
def test_create_game_rejects_bad_input(client, body, error):
    response = client.post("/api/games", json=body)
    assert response.status_code == 400
    assert response.json == {"error": error}


@pytest.mark.parametrize("language", ["en", "ar"])
def test_player_wins_and_sees_the_answer(client, language):
    secret = SECRET[language]
    game_id = new_game(client, language, secret)
    miss = wrong_words(language, secret, 1)[0]

    first = client.post(f"/api/games/{game_id}/guess", json={"word": miss}).json
    assert first["status"] == "playing"
    assert "answer" not in first  # the secret stays hidden while playing
    assert first["guesses"] == [{"word": miss, "feedback": get_feedback(miss, secret)}]

    final = client.post(f"/api/games/{game_id}/guess", json={"word": secret}).json
    assert final["status"] == "won"
    assert final["answer"] == secret
    assert final["guesses"][-1]["feedback"] == ["green"] * 5


def test_player_loses_after_six_misses(client):
    game_id = new_game(client, "en", "crane")
    for word in wrong_words("en", "crane", 6):
        state = client.post(f"/api/games/{game_id}/guess", json={"word": word}).json
    assert state["status"] == "lost"
    assert state["answer"] == "crane"

    response = client.post(f"/api/games/{game_id}/guess", json={"word": "crane"})
    assert response.status_code == 409
    assert response.json == {"error": "game_over"}


def test_retried_guess_is_not_counted_twice(client):
    game_id = new_game(client, "en", "crane")
    first = client.post(f"/api/games/{game_id}/guess", json={"word": "slate", "row": 0}).json
    retry = client.post(f"/api/games/{game_id}/guess", json={"word": "slate", "row": 0}).json
    assert retry == first
    assert len(retry["guesses"]) == 1


def test_retried_final_guess_returns_the_result(client):
    game_id = new_game(client, "en", "crane")
    client.post(f"/api/games/{game_id}/guess", json={"word": "slate", "row": 0})
    won = client.post(f"/api/games/{game_id}/guess", json={"word": "crane", "row": 1}).json
    retry = client.post(f"/api/games/{game_id}/guess", json={"word": "crane", "row": 1})
    assert retry.status_code == 200
    assert retry.json == won and won["answer"] == "crane"
    # a new guess after the game ended is still refused
    assert client.post(f"/api/games/{game_id}/guess", json={"word": "slate", "row": 2}).status_code == 409


def test_guess_is_validated(client):
    game_id = new_game(client)
    assert client.post(f"/api/games/{game_id}/guess", json={"word": "cra"}).json == {"error": "not_enough_letters"}
    assert client.post(f"/api/games/{game_id}/guess", json={"word": "qqqqq"}).json == {"error": "not_in_word_list"}
    # upper case and spaces are fine
    assert client.post(f"/api/games/{game_id}/guess", json={"word": " SLATE "}).json["guesses"][0]["word"] == "slate"


def test_unknown_game_and_agent(client):
    assert client.post("/api/games/nope/guess", json={"word": "crane"}).status_code == 404
    game_id = new_game(client)
    response = client.post(f"/api/games/{game_id}/agents/Nope/step")
    assert response.status_code == 400
    assert response.json == {"error": "unknown_agent"}
    assert client.post(f"/api/games/{game_id}/hint", json={"agent": "Nope"}).json == {"error": "unknown_agent"}


def test_random_secret_is_not_revealed(client):
    response = client.post("/api/games", json={"language": "en"})
    assert set(response.json) == {"id", "language", "max_guesses"}


@pytest.mark.parametrize("agent", list(games.AGENTS))
def test_hint_fits_the_players_board(client, agent):
    game_id = new_game(client, "en", "crane")
    client.post(f"/api/games/{game_id}/guess", json={"word": "slate"})
    response = client.post(f"/api/games/{game_id}/hint", json={"agent": agent})
    assert response.status_code == 200
    hint = response.json["word"]
    assert hint in WORDS["en"] and hint != "slate"
    if agent != "Entropy":  # Entropy may probe with any word; the others pick from the remaining candidates
        assert get_feedback("slate", hint) == get_feedback("slate", "crane")


@pytest.mark.parametrize("language", ["en", "ar"])
@pytest.mark.parametrize("agent", list(games.AGENTS))
def test_agent_solves_the_same_word(client, agent, language):
    secret = SECRET[language]
    game_id = new_game(client, language, secret)
    run = client.post(f"/api/games/{game_id}/agents/{agent}/solve").json

    assert run["status"] in ("won", "lost")
    assert 1 <= len(run["guesses"]) <= 6
    for guess in run["guesses"]:
        assert guess["feedback"] == get_feedback(guess["word"], secret)
    won = run["guesses"][-1]["word"] == secret
    assert run["status"] == ("won" if won else "lost")

    # a retry after a lost answer gets the finished board back, without playing on
    for action in ("solve", "step"):
        assert client.post(f"/api/games/{game_id}/agents/{agent}/{action}").json == run


def test_agent_steps_one_guess_at_a_time(client):
    game_id = new_game(client, "en", "crane")
    first = client.post(f"/api/games/{game_id}/agents/CSP/step").json
    assert len(first["guesses"]) == 1
    if first["status"] == "playing":
        assert first["candidates_left"] < len(WORDS["en"])
        second = client.post(f"/api/games/{game_id}/agents/CSP/step").json
        assert second["guesses"][0] == first["guesses"][0]
        assert len(second["guesses"]) == 2


def test_agents_play_independently_of_the_player(client):
    game_id = new_game(client, "en", "crane")
    client.post(f"/api/games/{game_id}/agents/Frequency/solve")
    state = client.post(f"/api/games/{game_id}/guess", json={"word": "slate"}).json
    assert [g["word"] for g in state["guesses"]] == ["slate"]


def test_old_games_are_dropped(client, monkeypatch):
    monkeypatch.setattr(games, "MAX_GAMES", 2)
    first = new_game(client)
    new_game(client)
    new_game(client)
    assert client.post(f"/api/games/{first}/guess", json={"word": "slate"}).status_code == 404
