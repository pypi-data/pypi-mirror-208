from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList


class IndexExtra(ConnectionBase):

	def showIndex(self, request: ULTIPA_REQUEST.ShowIndex = None,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListIndex:
		'''
		:param requestConfig:
		:EXP: conn.showIndex(ULTIPA_REQUEST.ShowIndex())
		:param request: ULTIPA_REQUEST
		:return:
		'''
		if request:
			command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.showNodeIndex or CommandList.showEdgeIndex
		else:
			command = CommandList.showIndex
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker, isSingleOne=False)
		return res

	def showFulltext(self, request: ULTIPA_REQUEST.ShowFulltext = None,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListIndex:
		'''
		:param requestConfig:
		:EXP: conn.showIndex(ULTIPA_REQUEST.ShowIndex())
		:param request: ULTIPA_REQUEST
		:return:
		'''
		if request:
			command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.showNodeFulltext or CommandList.showEdgeFulltext
		else:
			command = CommandList.showFulltext
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker, isSingleOne=False)
		return res

	def createIndex(self, request: ULTIPA_REQUEST.CreateIndex,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.createIndex(ULTIPA_REQUEST.CreatIndex(node_property='name'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.createNodeIndex or CommandList.createEdgeIndex
		commandP = request.toString
		uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=requestConfig)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def createFulltext(self, request: ULTIPA_REQUEST.CreateFulltext,
					   rquestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.createNodeFulltext or CommandList.createEdgeFulltext
		commandP = [request.toString, request.name]
		uqlMaker = UQLMAKER(command=command, commonParams=rquestConfig)
		uqlMaker.setCommandParams(commandP=commandP)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def dropIndex(self, request: ULTIPA_REQUEST.DropIndex,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.dropIndex(ULTIPA_REQUEST.DropIndex(node_property='node'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.dropNodeIndex or CommandList.dropEdgeIndex
		commandP = request.toString

		uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=requestConfig)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def dropFulltext(self, request: ULTIPA_REQUEST.DropFulltext,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		command = request.DBtype == ULTIPA.DBType.DBNODE and CommandList.dropNodeFulltext or CommandList.dropEdgeFulltext
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.fulltextName)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res
