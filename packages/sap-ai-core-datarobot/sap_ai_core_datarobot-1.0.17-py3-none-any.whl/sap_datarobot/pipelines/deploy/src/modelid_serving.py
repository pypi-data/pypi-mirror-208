from datarobot_predict.scoring_code import ScoringCodeModel
import pandas as pd
from flask import Flask, request
import os
import datarobot as dr


app = Flask(__name__)
model = None

def setup_app():
    global model
    project_id = os.getenv("PROJECT_ID")
    model_id = os.getenv("MODEL_ID")
    endpoint = os.getenv("ENDPOINT")
    token = os.getenv("TOKEN")
    print("Getting the Model...")
    dr.Client(endpoint=endpoint, token=token)
    model_jar = dr.models.Model(id=model_id, project_id=project_id)
    model_jar.download_scoring_code('/app/src/model.jar')
    print("Successful...")
    print("Loading Model...")
    model = ScoringCodeModel('/app/src/model.jar')
    print("Model has been Loaded....")
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


@app.route("/v1/models/model:predict", methods=["POST"])
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