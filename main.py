import random
import typing
import logging
import git
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


def returnMove(nextMove):
    return {"move": nextMove}


def checkWallCollision(possibleMoves, myHead, boardWidth, boardHeight):
    if myHead["x"] == 0:  # Head is at the left edge, don't move left
        possibleMoves["left"] = "false"
    if myHead["x"] == boardWidth - 1:  # Head is at the right edge, don't move right
        possibleMoves["right"] = "false"
    if myHead["y"] == 0:  # Head is at the bottom edge, don't move down
        possibleMoves["down"] = "false"
    if myHead["y"] == boardHeight - 1:  # Head is at the top edge, don't move up
        possibleMoves["up"] = "false"


def move(gameState: typing.Dict) -> typing.Dict:
    boardGrid = []
    for i in range(0, 11):
        boardGrid.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    possibleMoves = {"up": "true", "down": "true", "left": "true", "right": "true"}

    myHead = gameState["you"]["body"][0]
    myNeck = gameState["you"]["body"][1]

    boardWidth = gameState['board']['width']
    boardHeight = gameState['board']['height']

    if myNeck["x"] < myHead["x"]:  # Neck is left of head, don't move left
        possibleMoves["left"] = "false"

    elif myNeck["x"] > myHead["x"]:  # Neck is right of head, don't move right
        possibleMoves["right"] = "false"

    elif myNeck["y"] < myHead["y"]:  # Neck is below head, don't move down
        possibleMoves["down"] = "false"

    elif myNeck["y"] > myHead["y"]:  # Neck is above head, don't move up
        possibleMoves["up"] = "false"

    checkWallCollision(possibleMoves, myHead, boardWidth, boardHeight)
    # return a move
    safeMoves = []
    for move, status in possibleMoves.items():
        if status == "true":
            safeMoves.append(move)

    nextMove = random.choice(safeMoves)
    print(f"MOVE {gameState['turn']}: {nextMove}")

    return returnMove(nextMove)


app = Flask("Battlesnake")


def run_server(handlers: typing.Dict):
    @app.get("/")
    def on_info():
        return handlers["info"]()

    @app.post("/git-update")
    def git_update():
        repo = git.Repo("/home/anshmunjapara/battlesnake")
        origin = repo.remotes.origin
        repo.create_head("main", origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
        origin.pull()
        return "", 200

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
