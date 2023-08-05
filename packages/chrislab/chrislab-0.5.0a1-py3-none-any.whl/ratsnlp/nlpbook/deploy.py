from flask import Flask, request, jsonify, render_template


def get_web_service_app(inference_fn, template_file, ngrok_home=None):
    app = Flask(__name__, template_folder='')
    if ngrok_home:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app, home=ngrok_home)
    else:
        from flask_cors import CORS
        CORS(app)

    @app.route('/')
    def index():
        return render_template(template_file)

    @app.route('/api', methods=['POST'])
    def api():
        query_sentence = request.json
        output_data = inference_fn(query_sentence)
        response = jsonify(output_data)
        return response

    return app
