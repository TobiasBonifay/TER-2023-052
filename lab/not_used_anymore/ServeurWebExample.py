from flask import Flask, request, jsonify

app = Flask(__name__)

fake_db = {}


@app.route('/data', methods=['GET'])
def get_data():
    data_list = [value for key, value in fake_db.items()]
    return jsonify(data_list)


@app.route('/data', methods=['PUT'])
def put_data():
    data = request.get_json()
    for key, value in data.items():
        fake_db[key] = value
    return jsonify({"message": "Data stored successfully."}), 201


@app.route('/compute', methods=['GET'])
def compute():
    big_list = [i for i in range(1000000)]
    return jsonify({"message": f"Computed {len(big_list)} items."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
