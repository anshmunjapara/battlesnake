import random
import typing
import logging
from flask import Flask
from flask import request


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#f7eb0a",  # TODO: Choose color
        "head": "caffeine",  # TODO: Choose head
        "tail": "sharp",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def move(game_state: typing.Dict) -> typing.Dict:
    boardGrid = []
    for i in range(0, 11):
        boardGrid.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    safeMoves = {"up": "true", "down": "true", "left": "true", "right": "true"}

    # return a move
    nextMove = {"move": "up"}
    print(f"MOVE {game_state['turn']}: {nextMove}")

    return {"move": nextMove}


app = Flask("Battlesnake")


def run_server(handlers: typing.Dict):
    @app.get("/")
    def on_info():
        return handlers["info"]()

    @app.post("/start")
    def on_start():
        game_state = request.get_json()
        handlers["start"](game_state)
        return "ok"

    @app.post("/move")
    def on_move():
        game_state = request.get_json()
        return handlers["move"](game_state)

    @app.post("/end")
    def on_end():
        game_state = request.get_json()
        handlers["end"](game_state)
        return "ok"

    @app.after_request
    def identify_server(response):
        response.headers.set(
            "server", "battlesnake/github/starter-snake-python"
        )
        return response

    logging.getLogger("werkzeug").setLevel(logging.ERROR)


run_server({"info": info, "start": start, "move": move, "end": end})
