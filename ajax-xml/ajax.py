import math
import os
import json

from flask import Flask, request
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/ajax-handler', methods=['POST'])
def handler():
  payload = request.data
  json_request = json.loads(payload)
  expression = json_request['expression'] or '1+1' # default expression is 1+1
  print(type(expression))
  print(expression)
  mystring = ""
  mywords = expression.split(" ")
  print(mywords)
  data = json.loads('''
        [{''' +'''
			"id" : "{}",
			"name" : "{}",
			"category" : "{}",
			"color" : "{}"'''.format(str(mywords[0]),str(mywords[1]), str(mywords[2]), str(mywords[3]))+
		'''},
		{"id" : "001","name" : "apple","category" : "fruit","color" : "red"},
        {
			"id" : "002",
			"name" : "melon",
			"category" : "fruit",
			"color" : "green"
		},
		{
			"id" : "003",
			"name" : "banana",
			"category" : "fruit",
			"color" : "yellow"
		}]''');
  body = data
  return json.dumps(body), 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8765)