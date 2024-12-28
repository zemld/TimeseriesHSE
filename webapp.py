from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('index.html')

@app.route('/get-parameters', methods=['POST'])
def get_parameters():
    parameters = request.json
    category = parameters.get('category')
    value = parameters.get('value')
    start_date = parameters.get('start_date')
    end_date = parameters.get('end_date')
    print(category, value, start_date, end_date, sep='\n')
    return jsonify({'status': 'success',
                    'message': 'Однажды график точно будет построен!'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)