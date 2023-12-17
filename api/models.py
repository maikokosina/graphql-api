from mongoengine import Document
from mongoengine.fields import IntField, StringField, DictField

class Page(Document):
	meta = {'collection': 'pages'}
	page_id = IntField()
	owner_id = IntField()
	tag = StringField()
	title = StringField()
	description = StringField()
	keywords = StringField()
	body = StringField()
	files = DictField()
	
	def to_dict(self):
		return {
			"page_id": self.page_id,
			"owner_id": self.owner_id,
			"tag": self.tag,
			"title": self.title,
			"description": self.description,
			"keywords": self.keywords,
			"body": self.body,
			"files": self.files
		}
