#!venv/bin/python

import hashlib
import json
from api import models
from api.models import Page
from flask import Flask, request, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from mongoengine import connect
from pymongo import MongoClient

app = Flask(__name__)
auth = HTTPBasicAuth()

connect(host="mongodb://127.0.0.1:27017/archive")

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.archive
users = db.users
pages = db.pages
access = db.access
files = db.files

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	passmd5 = hashlib.md5(password.encode('utf-8')).hexdigest() 
	user_auth = users.find_one({"user_name": username, "password": passmd5.upper()},{ "_id": 0, "avatar": 0})
	print(user_auth)
	if user_auth['user_name'] == username:
		print(username)
		return username
	else:
		abort(401)

@auth.error_handler
def unauthorized():
	return make_response(jsonify({'message': 'Unauthorized access'}), 401)
	
@app.errorhandler(403)
def forbidden(error):
	return make_response(jsonify({'message': 'Forbidden'}), 403)

def getPages_resolver(obj, info):
	try:
		pages = list(Page.objects.filter(page_id__in=user_pages))
		print(pages)
		payload = {
			"success": True,
			"pages": pages
		}
	except Exception as error:
		payload = {
			"success": False,
			"errors": [str(error)]
		}
	return payload
	
def getPage_resolver(obj, info, page_id):
	try:
		pages = list(Page.objects.filter(page_id__in=user_pages))
		page = Page.objects.get(page_id=page_id)
		if page not in pages:
			abort(403)
		else:
			payload = {
			"success": True,
			"page": page.to_dict()
			}	
	except AttributeError:
		payload = {
			"success": False,
			"errors": ["Page with this id not found"]
		}
	return payload

query = ObjectType("Query")
query.set_field("getPages", getPages_resolver)
query.set_field("getPage", getPage_resolver)

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, query, snake_case_fallback_resolvers)

@app.route('/graphql', methods = ['GET'])
@auth.login_required
def graphql_playground():
	global user_name_query
	user_name_query = auth.current_user()
	return PLAYGROUND_HTML
	
@app.route('/graphql', methods = ['POST'])
def graphql_server():
	global user_pages
	user_pages = []
	for user in users.find({"user_name": user_name_query}):
		user_id = user['user_id']
	for access1 in access.find({"list": user_id, "privilege": "Read"},):
		user_pages.append(access1['page_id'])
	data = request.get_json()
	success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
	status_code = 200 if success else 400
	return jsonify(result), status_code
	
if __name__ == '__main__':
	app.run()
