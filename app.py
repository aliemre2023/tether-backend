from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

triangles = [[] for _ in range(24)]

def move(tri_id, dice_value):
    from_index = tri_id
    to_index = tri_id + dice_value

    if from_index < 0 or to_index >= len(triangles):
        return 0

    source_stack = triangles[from_index]
    target_stack = triangles[to_index]

    source_color = source_stack[-1]
    target_color = target_stack[-1]

    if not source_stack:
        return 0

    if (len(target_stack) == 0 or len(target_stack) == 1) or target_color == source_color:
        return 1

    return 0

@app.route('/api/reset', methods=['GET'])
def get_reset():
    for i in range(24):
        triangles[i] = []  # clear all first

    triangles[0] = ['white', 'white']
    triangles[5] = ['black'] * 5
    triangles[7] = ['black'] * 3
    triangles[11] = ['white'] * 5
    triangles[12] = ['black'] * 5
    triangles[16] = ['white'] * 3
    triangles[18] = ['white'] * 5
    triangles[23] = ['black'] * 2

    return jsonify({"board": triangles})

@app.route('/api/move', methods=['POST'])
def get_move():
    data = request.get_json()

    try:
        triangle_id = int(data.get("tri_id"))
        dice_1 = int(data.get("dice1"))
        dice_2 = int(data.get("dice2"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    moves = []

    if move(triangle_id, dice_1):
        moves.append(triangle_id + dice_1)
    if move(triangle_id, dice_2):
        moves.append(triangle_id + dice_2)
    if move(triangle_id, dice_1 + dice_2):
        moves.append(triangle_id + dice_1 + dice_2)

    return jsonify({"moves": moves})

@app.route('/api/board', methods=['GET'])
def get_board():
    board_state = [{"index": i, "stack": triangles[i]} for i in range(24)]
    return jsonify({"board": board_state})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
