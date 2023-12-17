import graphene
from graphene.relay import Node
from graphene_mongo import MongoengineObjectType
from models import Page as PageModel

class Page(MongoengineObjectType):

	class Meta:
		model = PageModel
		filter_fields = ['page_id']
		interfaces = (Node,)
		
class Query(graphene.ObjectType):

	pages = graphene.List(Page)
	
	def resolve_get_pages(self, info):
		return list(PageModel.objects.all())
		
	idpage = graphene.Field(Page, Id=graphene.Int())
	
	def resolve_get_page(parent, info, Id):
		return PageModel.objects.get(page_id=Id)
		
schema = graphene.Schema(query=Query)
