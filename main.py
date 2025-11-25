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


def checkBodyCollisions(possibleMoves, allBodiesCoords, myHead):
    directions = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    for direction, (dx, dy) in directions.items():
        newHead = (myHead["x"] + dx, myHead["y"] + dy)

        if newHead in allBodiesCoords:
            possibleMoves[direction] = "false"

    print("after checking self and enemy collision")
    print(possibleMoves)


def checkOneStepFutureCollision(possibleMoves, enemyHeads, myHead, enemyLength, myLength):
    directions = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    for head in enemyHeads:
        dangerous_positions = [
            (head[0] + 1, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1),
        ]

        for direction, (dx, dy) in directions.items():
            if possibleMoves[direction] == "true":
                if (myHead["x"] + dx, myHead["y"] + dy) in dangerous_positions:
                    if myLength > enemyLength[head]:
                        possibleMoves[direction] = "kill"
                    else:
                        possibleMoves[direction] = "maybe"
                else:
                    possibleMoves[direction] = "true"
    print("after checking future 1 step collision")
    print(possibleMoves)


def move(gameState: typing.Dict) -> typing.Dict:
    boardGrid = []
    for i in range(0, 11):
        boardGrid.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    possibleMoves = {"up": "true", "down": "true", "left": "true", "right": "true"}

    myHead = gameState["you"]["body"][0]
    myNeck = gameState["you"]["body"][1]
    myBody = gameState["you"]["body"]
    myLength = gameState["you"]["length"]
    opponents = gameState["board"]["snakes"]
    enemyCoords = set()
    enemyHeads = []
    enemyLength = {}

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

    for snake in opponents:
        enemyHead = (snake["head"]["x"], snake["head"]["y"])
        for segment in snake["body"][:-1]:
            enemyCoords.add((segment["x"], segment["y"]))
        if enemyHead != (myHead['x'], myHead['y']):
            enemyHeads.append(enemyHead)
            enemyLength[enemyHead] = snake["length"]

    checkWallCollision(possibleMoves, myHead, boardWidth, boardHeight)
    checkBodyCollisions(possibleMoves, enemyCoords, myHead)
    checkOneStepFutureCollision(possibleMoves, enemyHeads, myHead, enemyLength, myLength)
    # return a move
    safeMoves = []
    maybeSafeMoves = []
    killerMoves = []

    for move, status in possibleMoves.items():
        if status == "true":
            safeMoves.append(move)
        elif status == "maybe":
            maybeSafeMoves.append(move)
        elif status == "kill":
            killerMoves.append(move)
    nextMove = None
    if killerMoves:
        nextMove = random.choice(killerMoves)
    elif safeMoves:
        nextMove = random.choice(safeMoves)
    elif maybeSafeMoves:
        nextMove = random.choice(maybeSafeMoves)

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
