
import sys,os
import subprocess
import shutil
from wasteDetection.pipeline.training_pipeline import TrainPipeline
from wasteDetection.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response
from flask_cors import CORS, cross_origin
from wasteDetection.constant.application import APP_HOST, APP_PORT


app = Flask(__name__)
CORS(app)

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"



@app.route("/train")
def trainRoute():
    obj = TrainPipeline()
    obj.run_pipeline()
    return "Training Successfull!!" 


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/predict", methods=['POST','GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']
        decodeImage(image, clApp.filename)

        # Run YOLOv5 detection with lower confidence threshold
        # Use data.yaml if it exists in artifacts, otherwise let model use embedded classes
        data_yaml_path = "artifacts/data_ingestion/feature_store/data.yaml"
        
        # Change to yolov5 directory and run detection
        if os.path.exists(data_yaml_path):
            cmd = [sys.executable, "detect.py", "--weights", "best.pt", "--img", "416", 
                   "--conf", "0.25", "--source", "../data/inputImage.jpg", "--data", f"../{data_yaml_path}"]
        else:
            cmd = [sys.executable, "detect.py", "--weights", "best.pt", "--img", "416", 
                   "--conf", "0.25", "--source", "../data/inputImage.jpg"]
        
        print(f"Running detection: {' '.join(cmd)}")
        subprocess.run(cmd, cwd="yolov5", check=True)

        # Encode the result image
        result_path = "yolov5/runs/detect/exp/inputImage.jpg"
        if os.path.exists(result_path):
            opencodedbase64 = encodeImageIntoBase64(result_path)
            result = {"image": opencodedbase64.decode('utf-8')}
        else:
            print(f"Result image not found at {result_path}")
            # Return original image if detection failed
            opencodedbase64 = encodeImageIntoBase64("data/inputImage.jpg")
            result = {"image": opencodedbase64.decode('utf-8'), "warning": "No detections found"}
        
        # Cleanup runs directory (Windows compatible)
        if os.path.exists("yolov5/runs"):
            shutil.rmtree("yolov5/runs")

    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    except KeyError:
        return Response("Key value error incorrect key passed")
    except Exception as e:
        print(f"Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": str(e)}

    return jsonify(result)



@app.route("/live", methods=['GET'])
@cross_origin()
def predictLive():
    try:
        os.system("cd yolov5/ && python detect.py --weights my_model.pt --img 416 --conf 0.5 --source 0")
        os.system("rm -rf yolov5/runs")
        return "Camera starting!!" 

    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    



if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host=APP_HOST, port=APP_PORT)
