from flask_cors import CORS #allow cross origin on the frontend because basically not every backend allows anybody to call them
import requests
from flask import Flask, flash, request, jsonify, make_response #flask is for creating our own API
from decouple import config #to get values inside our .env file which are our credentials
import io
import os
import json
from google.cloud import vision #to use the functions inside the google cloud api
from werkzeug.utils import secure_filename #validate the filename


UPLOAD_FOLDER = 'Images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.json_encoder  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Imports the Google Cloud client library
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'cred.json'

CORS(app, resources={r"/*": {"origins": "*"}}) #sets the CORS to all origins are accepted

#to check filename and check if its in the ALLOWED_EXTENSIONS above
def allowed_file(filename): 
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#this is our own first API url using flask



@app.route('/')
def hello_world():
    return 'Hello from Flask!'

#when a person does /search
#it will take the file object that is sent through that request
#check if file is allowed then save the file inside the images folder
#then calls the google cloud api to read what are the labels and search each label through the calorie ninja API
#and return the labels info
@app.route('/search', methods=['POST'])
def searchCommand():
    file = request.files.get('file', None)
    print(file.filename)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print("saved")

    query = []
    query = ReadLabel(".\Images\my-photo.png")
    labels = []
    for label in query:
        food = SearchCalorieNinja(label.description)
        if (food == '{"items": []}'):
            print("Empty")
        else:
            labels.append(json.loads(food))
            # foodObj  = json.loads(food)
            # file1 = open('.\dfood.txt','r')
            # lines = file1.readlines()
            # print(foodObj['items'])
            # for line in lines:
            #     for j in foodObj['items']:
            #         print(j)
            #         if j['name'] == line: 
            #             print(line)
            #             labels.append(json.loads(food))
            #             break
    return jsonify(labels)



#called in the API function above to use the calorie ninja url, add our key and if the response is ok, then it will return the data, or else it will print an error
def SearchCalorieNinja(query):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    response = requests.get(api_url + query, headers={'X-Api-Key': config('CalorieNinja')})
    if response.status_code == requests.codes.ok:
        return(response.text)
    else:
        print("Error:", response.status_code, response.text)

        
        
       
#read label, open the image in the specified path, then send it to google vision and return the list of labels
def ReadLabel(path):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.abspath(path)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # print('Labels:')
    # for label in labels:
    #     print(label.description)

    return labels

