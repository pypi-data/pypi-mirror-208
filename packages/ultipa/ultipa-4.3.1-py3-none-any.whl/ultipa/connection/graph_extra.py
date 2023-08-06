import json

from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.ResposeFormat import ResponseKeyFormat

REPLACE_KEYS = {
	"graph": "name",
}


class GraphExtra(ConnectionBase):

	def listGraph(self,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListGraph:
		return self.showGraph(requestConfig)

	def showGraph(self,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListGraph:
		uqlMaker = UQLMAKER(command=CommandList.showGraph, commonParams=requestConfig)
		# uqlMaker.addParam('graph',"",required=False)
		uqlMaker.setCommandParams("")
		res = self.UqlListSimple(self, uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS))
		return res

	def getGraph(self, request: ULTIPA_REQUEST.Graph,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseGraph:
		# uqlMaker = UQLMAKER(command=CommandList.showGraph,commandP=json.dumps(request.graphSetName, ensure_ascii=False),commonParams=requestConfig)
		uqlMaker = UQLMAKER(command=CommandList.showGraph, commonParams=requestConfig)
		# uqlMaker.addParam('graph',request.graphSetName)
		uqlMaker.setCommandParams(request.graph)

		res = self.UqlListSimple(self, uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS))
		if res.status.code == ULTIPA.Code.SUCCESS and res.data != None and len(res.data) > 0:
			res.data = res.data[0]
		return res

	def createGraph(self, request: ULTIPA_REQUEST.Graph,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		uqlMaker = UQLMAKER(command=CommandList.createGraph, commonParams=requestConfig)
		# uqlMaker.addParam('graph',request.graphSetName)
		if request.description:
			uqlMaker.setCommandParams([request.graph, request.description])
		else:
			uqlMaker.setCommandParams(request.graph)
		res = self.uqlSingle(uqlMaker)
		return res

	def dropGraph(self, request: ULTIPA_REQUEST.Graph,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		uqlMaker = UQLMAKER(command=CommandList.dropGraph, commonParams=requestConfig)
		# uqlMaker.addParam('graph',request.graphSetName)
		uqlMaker.setCommandParams(request.graph)
		res = self.uqlSingle(uqlMaker)
		return res

	def alterGraph(self, request: ULTIPA_REQUEST.AlterGraph,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		requestConfig.graphName = request.oldGraphName
		uqlMaker = UQLMAKER(command=CommandList.alterGraph, commonParams=requestConfig)
		# uqlMaker.addParam('graph', request.oldGraphSetName)
		uqlMaker.setCommandParams(request.oldGraphName)
		data = {"name": request.newGraphName}
		if request.newDescription is not None:
			data.update({'description': request.newDescription})
		uqlMaker.addParam("set", data)
		res = self.uqlSingle(uqlMaker)
		return res
