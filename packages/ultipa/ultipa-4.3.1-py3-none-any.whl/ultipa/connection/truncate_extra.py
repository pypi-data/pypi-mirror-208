from ultipa.types.types import TruncateType
from ultipa.connection.connection_base import ConnectionBase
from ultipa.utils import UQLMAKER, CommandList
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE

JSONSTRING_KEYS = ["graph_privileges", "system_privileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']


class TruncateExtra(ConnectionBase):

	def truncate(self, request: ULTIPA_REQUEST.Truncate,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		command = CommandList.truncate
		requestConfig.graphName = request.graphSetName
		uqlMaker = UQLMAKER(command, commonParams=requestConfig)
		uqlMaker.addParam("graph", request.graphSetName)
		if request.dbType:
			if request.dbType == TruncateType.NODES:
				if request.all:
					uqlMaker.addParam("nodes", "*")
				if not request.all and request.schema:
					uqlMaker.addParam("nodes", "@" + request.schema, notQuotes=True)
			if request.dbType == TruncateType.EDGES:
				if request.all:
					uqlMaker.addParam("edges", "*")
				if not request.all and request.schema:
					uqlMaker.addParam("edges", "@" + request.schema, notQuotes=True)

		# if request.all and not request.dbType:
		#     uqlMaker = UQLMAKER(command,commandP=request.dbType,commonParams=requestConfig)

		return ConnectionBase.UqlUpdateSimple(self, uqlMaker)

	def compact(self, request: ULTIPA_REQUEST.Graph,
				requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		command = CommandList.compact
		uqlMaker = UQLMAKER(command, commonParams=requestConfig)
		uqlMaker.addParam("graph", request.graph)
		return ConnectionBase.UqlUpdateSimple(self, uqlMaker)

	def mount(self, request: ULTIPA_REQUEST.Mount,
			  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		commonP = []
		if request.graph:
			commonP = request.graph
			requestConfig.graphName = request.graph
		uqlMaker = UQLMAKER(command=CommandList.mount, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commonP)
		return self.UqlUpdateSimple(self, uqlMaker)

	def unmount(self, request: ULTIPA_REQUEST.Unmount,
				requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		commonP = []
		if request.graph:
			commonP = request.graph
			requestConfig.graphName = request.graph
		uqlMaker = UQLMAKER(command=CommandList.unmount, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commonP)
		return self.UqlUpdateSimple(self, uqlMaker)
