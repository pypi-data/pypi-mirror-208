import json

from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA, ULTIPA_REQUEST, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertTableToDict

BOOL_KEYS = ["index", "lte"]
REPLACE_KEYS = {
	"name": "schemaName",
	"type": "propertyType",
}


class SchemaExtra(ConnectionBase):

	def createSchema(self, request: ULTIPA_REQUEST.CreateSchema,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):

		'''
		// create node schema
		create().node_schema("<name>", "<description>");

		// create edge schema
		create().edge_schema("<name>", "<description>");
		:return:
		'''

		command = request.type == ULTIPA.DBType.DBNODE and CommandList.createNodeSchema or CommandList.createEdgeSchema
		commandP = [request.schemaName]
		if request.description:
			commandP.append(request.description)
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commandP)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def listSchema(self, request: ULTIPA_REQUEST.ShowSchema = None,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		return self.showSchema(request, requestConfig)

	def showSchema(self, request: ULTIPA_REQUEST.ShowSchema = None,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		// list all schema
		list().schema()

		// list node schema
		list().node_schema()

		// list edge schema()
		list().edge_schema()

		'''
		if request:
			if request.schemaType == ULTIPA.DBType.DBNODE:
				command = CommandList.showNodeSchema
			elif request.schemaType == ULTIPA.DBType.DBEDGE:
				command = CommandList.showEdgeSchema
			else:
				command = CommandList.showSchema

			if request.schemaName:
				commandP = '@' + request.schemaName
			else:
				commandP = ''
		else:
			command = CommandList.showSchema
			commandP = ''

		uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=requestConfig)
		# res = self.UqlListSimple(self, uqlMaker=uqlMaker,
		#                          responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS,jsonKeys=["properties"]),isSingleOne=False)
		# for data in res.data:
		#     if data.name == "_nodeSchema":
		#         for scheam in data.data:
		#             scheam.type = "Node"
		#     if data.name == "_edgeSchema":
		#         for scheam in data.data:
		#             scheam.type = "Edge"
		res = self.uqlSingle(uqlMaker)
		return res

	def alterSchema(self, request: ULTIPA_REQUEST.AlterSchema,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		// alter a node schema
		alter().node_schema(@<schema>).set({name:"<name>", description:"<desc>"})

		// alter an edge schema
		alter().edge_schema(@<schema>).set({name:"<name>", description:"<desc>"})
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.alterNodeSchema or CommandList.alterEdgeSchema
		commandP = '@' + request.schemaName
		update_dict = {}
		if request.new_schemaName:
			update_dict.setdefault('name', request.new_schemaName)
		if request.description:
			update_dict.update({'description': request.description})
		uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=requestConfig)
		uqlMaker.addParam("set", update_dict)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def dropSchema(self, request: ULTIPA_REQUEST.DropSchema,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):

		'''
		// drop node schema
		drop().node_schema(@<schema>)

		// drop edge schema
		drop().edge_schema(@<schema>)
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.dropNodeSchema or CommandList.dropEdgeSchema
		commandP = '@' + request.schemaName

		uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=requestConfig)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res
