from .models import Page
from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.archive
users = db.users
pages = db.pages
access = db.access
files = db.files

username_query = 'Liza'
user_pages = []

for user in users.find({"user_name": username_query}):
	user_id = user['user_id']
for access1 in access.find({"list": user_id, "privilege": "Read"},):
	user_pages.append(access1['page_id'])

def getPages_resolver(obj, info, user_name):
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
		page = Page.objects.get(page_id=page_id)
		payload = {
			"success": True,
			"page": page.to_dict()
		}
	except AttributeError:
		payload = {
			"success": False,
			"errors": ["Page with id {page_id} not found"]
		}
	return payload
