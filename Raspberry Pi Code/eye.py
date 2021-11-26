# TODO(developer): Uncomment and set the following variables
project_id = 'safewheel-219707'
compute_region = 'us-central1'
#model_id = 'ICN7054792989205252357'
model_id = 'ICN3677476150927345517'
file_path = '/home/pi/image.jpg'
score_threshold = '0.5'

from google.cloud import storage
from google.cloud import automl_v1beta1 as automl
import os
import picamera
import datetime
import time as t
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)


def takephoto():
    camera = picamera.PiCamera()
    camera.capture('image.jpg')
    camera.close()
    
def getTime():
    now = str(datetime.datetime.now())
    with open("eye-time.txt","a+") as f:
        f.write('|')
        f.write(now)
    f.close()
    
def main():
    	os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/SAFEWheel-e3260c10b7e8.json"
    	project = 'safewheel-219707'
    	storage_client = storage.Client(project=project)
    	bucket = storage_client.get_bucket('safewheel_data')

    	automl_client = automl.AutoMlClient()
    	# Get the full path of the model.
    	model_full_id = automl_client.model_path(
    	project_id, compute_region, model_id)   
    	prediction_client = automl.PredictionServiceClient()

	while True:
    	    takephoto()
    	    getTime()

    	    with open(file_path, "rb") as image_file:
    	        content = image_file.read()
   	    payload = {"image": {"image_bytes": content}}
    	    params = {}
    	    if score_threshold:
      	        params = {"score_threshold": score_threshold}

    	    response = prediction_client.predict(model_full_id, payload, params)
    	    print("Prediction results:")
    	    for result in response.payload:
                print("Predicted class name: {}".format(result.display_name))
                print("Predicted class score: {}".format(result.classification.score))
    
    	    #image = bucket.blob('Test Image')
	    #image.upload_from_filename('image.jpg')

	    if (result.display_name) == "Closed":
			time = bucket.blob('Eye Time')
            time.upload_from_filename('eye-time.txt')
			print("Buzzer!")
        	GPIO.output(27,GPIO.HIGH)       
        	t.sleep(0.5)
        	GPIO.output(27,GPIO.LOW)
        	t.sleep(0.5)
	    else:
		t.sleep(0.5)

    
if __name__ == '__main__':
    
    main()

