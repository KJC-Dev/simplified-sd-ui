
from flask import Flask, request, render_template,redirect,jsonify
import os
import json
import requests
import json
from PIL import Image
from io import BytesIO
import base64

url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
          }
previous_text_dict = {}
app = Flask(__name__)

def previous(visitor):
    if visitor in previous_text_dict:
        return previous_text_dict[visitor]
    else: 
        previous_text_dict[visitor] = ""
        return previous_text_dict[visitor]

@app.route('/')
def index():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            visitor=request.environ['REMOTE_ADDR']
    else:
            visitor=request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    print(previous_text_dict)

    return render_template('index.html', previous_text=previous(visitor))

#@app.after_request
#def after( response ): 
#    os.remove("static/output.png")
#    return response
@app.route('/submit', methods=['POST'])
def submit():

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            visitor=request.environ['REMOTE_ADDR']
    else:
            visitor=request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    
    previous_text_dict[visitor] = request.form['text']
    data = {
            "prompt": request.form['text'],
            "steps": 20
           }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    # Lo2ad the response JSON into a python dictionary
    response_dict = json.loads(response.text)

    # Extract base64 encoded image data from response JSON
    img_bytes = bytes(response_dict["images"][0], 'utf-8')

    # Convert the bytes to a binary format and open it using PIL
    img_bin = BytesIO(base64.b64decode(img_bytes))
    img = Image.open(img_bin)
    
    # Save the image into a file named "output.png" in the current directory
    img.save("static/output.png")

    app = Flask(__name__)
    return redirect("/", code=302)
if __name__=='__main__':
    app.run(host='0.0.0.0', port=3000)
