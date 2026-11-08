"""
Web app: serves the page in web/static and a small JSON API over web/game.py.

Run from the repository root:  python -m web.app
"""

import os

from flask import Flask, jsonify, request

from env.wordle_env import MAX_GUESSES, WordleEnv
from web import game as games

app = Flask(__name__)


@app.errorhandler(games.GameError)
def game_error(error):
    return jsonify(error=error.code), error.status


def json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/random-word")
def random_word():
    language = games.check_language(request.args.get("language"))
    return jsonify(word=WordleEnv(language).generate_random_word())


@app.post("/api/games")
def create_game():
    """Start a game. With "word" the secret is that word; without it, a hidden random one."""
    body = json_body()
    language = games.check_language(body.get("language"))
    word = games.check_word(body["word"], language) if "word" in body else None
    game = games.create_game(language, word)
    return jsonify(id=game.id, language=language, max_guesses=MAX_GUESSES), 201


@app.post("/api/games/<game_id>/guess")
def guess(game_id):
    body = json_body()
    return jsonify(games.get_game(game_id).guess(body.get("word"), body.get("row")))


@app.post("/api/games/<game_id>/hint")
def hint(game_id):
    agent = json_body().get("agent")
    return jsonify(agent=agent, word=games.get_game(game_id).hint(agent))


@app.post("/api/games/<game_id>/agents/<agent>/step")
def agent_step(game_id, agent):
    return jsonify(games.get_game(game_id).agent_step(agent))


@app.post("/api/games/<game_id>/agents/<agent>/solve")
def agent_solve(game_id, agent):
    return jsonify(games.get_game(game_id).agent_step(agent, until_done=True))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
