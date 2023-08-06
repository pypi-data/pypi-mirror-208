import json
from datarobot_predict.scoring_code import ScoringCodeModel
import pandas as pd
from flask import Flask, request
import os


app = Flask(__name__)
model = None

def setup_app():
    global model
    dirs = os.listdir("/mnt/models/")
    model_name = os.getenv("MODELS_STR", default='model') + ".jar"
    for file in dirs:
        print(file)
    print("Loading Model...")
    model_file_path = os.path.join("/mnt/models", model_name)
    print(model_file_path)
    model = ScoringCodeModel(model_file_path)
    print(type(model))
    print("Successful...")
    return model

@app.before_request
def load_model():
    global model
    if model is None:
        model = setup_app()
        print(model)


@app.route('/v1/status')
def index():
    global model
    if model is not None:
        return 'DataRobot model is ready for serving!'
    else:
        return 'Model is not loaded!'

@app.route("/v1/models/{}:predict".format(os.environ.get("MODELS_STR")), methods=["POST"])
def predict():
    global model
    input_dict_list = request.json
    inference_in_df = pd.DataFrame(input_dict_list)
    inference_out = model.predict(inference_in_df)
    result_json = inference_out.to_json(orient="records")
    output = {"predictions": result_json}
    return output

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=9001)
