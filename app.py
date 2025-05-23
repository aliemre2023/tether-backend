from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

triangles = [[] for _ in range(24)]
broken_white = 0
broken_black = 0

def move_white(from_index, dice_value):
    if not (0 <= from_index < 24):
        return 0

    source_stack = triangles[from_index]
    if not source_stack or source_stack[-1] != "white":
        return 0

    to_index = from_index + dice_value
    if to_index >= 24:
        return 0

    target_stack = triangles[to_index]
    target_color = target_stack[-1] if target_stack else None

    if (len(target_stack) <= 1 or target_color == "white"):
        return 1

    return 0

def move_black(from_index, dice_value):
    if not (0 <= from_index < 24):
        return 0

    source_stack = triangles[from_index]
    if not source_stack or source_stack[-1] != "black":
        return 0

    to_index = from_index - dice_value
    if to_index < 0:
        return 0

    target_stack = triangles[to_index]
    target_color = target_stack[-1] if target_stack else None

    if (len(target_stack) <= 1 or target_color == "black"):
        return 1

    return 0

@app.route('/api/reset', methods=['GET'])
def get_reset():
    global broken_white, broken_black
    broken_white = 0
    broken_black = 0

    for i in range(24):
        triangles[i] = []

    # Standard Backgammon-like setup
    triangles[0] = ['white', 'white']
    triangles[5] = ['black'] * 5
    triangles[7] = ['black'] * 3
    triangles[11] = ['white'] * 5
    triangles[12] = ['black'] * 5
    triangles[16] = ['white'] * 3
    triangles[18] = ['white'] * 5
    triangles[23] = ['black'] * 2

    return jsonify({"board": triangles})

@app.route('/api/board/reload', methods=['GET'])
def get_update_board():
    global broken_white, broken_black
    return jsonify({
        "board": triangles,
        "broken": [broken_white, broken_black]
    })

@app.route('/api/piece/save', methods=['POST'])
def get_save_moves():
    print("something in there")
    data = request.get_json()
    index = int(data.get("index"))
    dice1 = int(data.get("dice1"))
    dice2 = int(data.get("dice2"))

    available_places = []
    if(index == 101):
        places = [dice1 - 1, dice2 - 1, dice1 + dice2 - 1]
        for i in places:
            if(len(triangles[i]) == 0):
                available_places.append(i)
            elif(len(triangles[i]) == 1 and triangles[i][-1] == "black"):
                available_places.append(i)
            elif(triangles[i][-1] == "white"):
                available_places.append(i)

            
    if(index == 102):
        places = [24 - dice1, 24 - dice2, 24 - (dice1 + dice2)]
        for i in places:
            if(len(triangles[i]) == 0):
                available_places.append(i)
            elif(len(triangles[i]) == 1 and triangles[i][-1] == "white"):
                available_places.append(i)
            elif(triangles[i][-1] == "black"):
                available_places.append(i)

    return jsonify({
        "highlightedPlaces": available_places,
    })


@app.route('/api/move', methods=['POST'])
def get_move():
    data = request.get_json()

    try:
        triangle_id = int(data.get("index"))
        dice_1 = int(data.get("dice1"))
        dice_2 = int(data.get("dice2"))
        print("Triangle index: ", triangle_id)
        # Don't understand, it should be already come with true index value
        if(triangle_id > 5 and triangle_id <= 11):
            triangle_id = 11 - triangle_id + 6
        if(triangle_id > -1 and triangle_id <= 5):
            triangle_id = 5 - triangle_id       
        

    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    if not (0 <= triangle_id < 24):
        return jsonify({"error": "Invalid triangle index"}), 400

    source_stack = triangles[triangle_id]
    print("source_stack: ",source_stack)
    if len(source_stack) <= 0:
        return jsonify({"error": "Selected triangle is empty"}), 400

    color = source_stack[-1]
    moves = []

    if color == "white":
        if move_white(triangle_id, dice_1):
            moves.append(triangle_id + dice_1)
        if move_white(triangle_id, dice_2):
            moves.append(triangle_id + dice_2)
        if move_white(triangle_id, dice_1 + dice_2):
            moves.append(triangle_id + dice_1 + dice_2)

    elif color == "black":
        if move_black(triangle_id, dice_1):
            moves.append(triangle_id - dice_1)
        if move_black(triangle_id, dice_2):
            moves.append(triangle_id - dice_2)
        if move_black(triangle_id, dice_1 + dice_2):
            moves.append(triangle_id - (dice_1 + dice_2))

    return jsonify({"moves": moves})

@app.route('/api/moveTo', methods=['POST'])
def get_moveTo():
    global broken_white, broken_black

    data = request.get_json()
    print("Received data:", data)

   
    index_from = int(data.get("index_from"))
    index_to = int(data.get("index_to"))

    if(index_from > 5 and index_from <= 11):
        index_from = 11 - index_from + 6
    if(index_from > -1 and index_from <= 5):
        index_from = 5 - index_from

    if(index_to > 5 and index_to <= 11):
        index_to = 11 - index_to + 6
    if(index_to > -1 and index_to <= 5):
        index_to = 5 - index_to

    if(index_from == 101 or index_from == 102):
        if(index_from == 101):
            broken_white -= 1
            if(len(triangles[index_to]) == 0):
                triangles[index_to].append("white")
            elif(len(triangles[index_to]) == 1 and triangles[index_to][-1] == "black"):
                broken_black += 1
                triangles[index_to].pop()
                triangles[index_to].append("white")
            elif(triangles[index_to][-1] == "white"):
                triangles[index_to].append("white")
        if(index_from == 102):
            broken_black -= 1
            if(len(triangles[index_to]) == 0):
                triangles[index_to].append("black")
            elif(len(triangles[index_to]) == 1 and triangles[index_to][-1] == "white"):
                broken_white += 1
                triangles[index_to].pop()
                triangles[index_to].append("black")
            elif(triangles[index_to][-1] == "black"):
                triangles[index_to].append("black")
        return jsonify({"status": 200, "index_from": index_from, "index_to": index_to})


    # default broken status
    if(len(triangles[index_to]) == 1 and (triangles[index_from][-1] == "black" and triangles[index_to][-1] == "white")):
        print("HEYYYYYYYY")
        broken_white += 1
        triangles[index_to].pop()
    if(len(triangles[index_to]) == 1 and (triangles[index_from][-1] == "white" and triangles[index_to][-1] == "black")):
        print("HEYY0000000")
        broken_black += 1
        triangles[index_to].pop()

    if index_from < 0 or index_from >= 24 or index_to < 0 or index_to >= 24:
        return jsonify({"error": "Invalid indexes"}), 400

    if triangles[index_from]:
        piece = triangles[index_from].pop()
        triangles[index_to].append(piece)

        #for row in triangles:
        #    print(row, "\n")

        return jsonify({"status": 200, "moved_piece": piece, "index_from": index_from, "index_to": index_to})
    else:
        return jsonify({"error": "No piece to move at index_from"}), 400

    return jsonify({"status": 200})

@app.route('/api/board', methods=['GET'])
def get_board():
    board_state = [{"index": i, "stack": triangles[i]} for i in range(24)]
    return jsonify({"board": board_state})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
