from flask import Flask, request, jsonify
from model_func import ask, get_top_similar_texts, e5_embedding, ada_embedding
import json

app = Flask(__name__)
health_status = True


@app.route("/")
def hello():
    print('Hello, service started')


@app.route('/similar_rows', methods=['GET', 'POST'])
def find_rows():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return "No json body"
        try:
            query = data['query']
        except KeyError as err:
            return 'No query  provided'
        print('query  ---- > ', query)

        if data['emb_type'] is None or data['emb_type'] == 'ada':
            embed = ada_embedding(query)
        else:
            embed = e5_embedding(query)

        texts = get_top_similar_texts(embed)
        res = json.dumps({'tests': str(texts)})
        return res
    return 'Not a proper request method or data'


@app.route('/generate', methods=['GET', 'POST'])
def generate_resp():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return 'No json body'
        try:
            query = data['request']
        except KeyError as err:
            return 'No query provided'
        try:
            sources = data['sources']
        except KeyError as err:
            return 'No sources provided'
        answer = None
        while answer is None:
            try:
                answer = ask(query, sources)
            except:
                pass
        res = json.dumps({'result': answer})
        return res
    return 'Not a proper request method or data'


@app.route('/health')
def health():
    if health_status:
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500

    return resp


if __name__ == "__main__":
    print("application started")
    app.run(host='0.0.0.0', port=8081)
