from flask import Flask, render_template, request, url_for, jsonify

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('index.html')


@app.route('/chart-parameters', methods=['POST'])
def handle_parameters():
    parameters = request.json
    category = parameters.get('category')
    value = parameters.get('value')
    start_date = parameters.get('start_date')
    end_date = parameters.get('end_date')

    redirect_url = url_for('show_chart', category=category, value=value, start_date=start_date, end_date=end_date)
    return jsonify({'redirect': redirect_url})


@app.route('/chart')
def show_chart():
    return f"""<h1>График с {request.args.get('start_date')} по {request.args.get('end_date')} построен! 
    Параметр {request.args.get('category'), request.args.get('value')}.</h1>"""


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)